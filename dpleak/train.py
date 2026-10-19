"""
Fine-tune Llama-3.2-1B (4-bit nf4 + LoRA) with or without DP-SGD for one run of the grid.

    python -m dpleak.train --run i2b2_docs100_A_eps8_author_s42 --runs-dir runs

Hyper-parameters are those of the published runs (seq 1024, LoRA r=4/alpha=32 on
q/k/v/o, LR 3e-4 constant, weight decay 0.01, clip 1.0, effective batch 32).
Differences from the first submission, all deliberate:
  * one GPU per run (batch 16 x 2 accumulation steps) instead of 2-GPU DDP;
  * the number of optimisation steps is fixed to 12 record-level epochs,
    12 * floor(N/32) (480 on i2b2, 372 on MEDDOCAN), for every run, including
    author-level runs, so all models see the same number of sampled records;
  * the DP accountant composes exactly that number of steps;
  * the held-out split uses a fixed seed (42) for every training seed.
Writes {runs}/{id}/adapter_model.safetensors and run.json (privacy accounting,
losses, timing, versions).
"""
import argparse
import json
import logging
import math
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "vendor"))

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("WANDB_DISABLED", "true")

import torch  # noqa: E402
import transformers  # noqa: E402
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training  # noqa: E402

import dp_transformers  # noqa: E402
from dp_transformers.dp_utils import OpacusDPTrainer, create_author_mapping  # noqa: E402

from . import data, spec  # noqa: E402

BASE_MODEL = os.environ.get("DPLEAK_BASE_MODEL", "meta-llama/Llama-3.2-1B")
SEQ_LEN = 1024
EPOCHS = 12
BATCH = 32
logger = logging.getLogger("dpleak.train")


def bnb_config():
    return transformers.BitsAndBytesConfig(
        load_in_4bit=True, bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)


def git_commit():
    try:
        import subprocess
        return subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


@torch.no_grad()
def mean_nll(model, tok, texts, bs=4):
    """Token-level mean NLL of full notes (utility proxy, same truncation as training)."""
    model.eval()
    tot, n = 0.0, 0
    for i in range(0, len(texts), bs):
        enc = tok(texts[i:i + bs], return_tensors="pt", padding=True, truncation=True,
                  max_length=SEQ_LEN).to(model.device)
        logits = model(input_ids=enc.input_ids, attention_mask=enc.attention_mask).logits[:, :-1].float()
        tgt = enc.input_ids[:, 1:]
        m = enc.attention_mask[:, 1:].float()
        nll = torch.nn.functional.cross_entropy(logits.transpose(1, 2), tgt, reduction="none")
        tot += float((nll * m).sum())
        n += float(m.sum())
    return tot / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--runs-dir", default=str(REPO / "runs"))
    ap.add_argument("--per-device-batch", type=int, default=16)
    ap.add_argument("--max-steps", type=int, default=None, help="override (smoke tests only)")
    a = ap.parse_args()

    run = spec.parse_run_id(a.run)
    out = Path(a.runs_dir) / run.id
    out.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    t0 = time.time()
    transformers.set_seed(run.seed)

    tok = transformers.AutoTokenizer.from_pretrained(BASE_MODEL)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token

    ds = data.training_split(run.dataset, run.canary, run.exposure, run.tagset)
    train_authors = list(ds["train"]["author"])
    train_files = list(ds["train"]["file"])
    n_train = len(train_authors)
    steps = EPOCHS * (n_train // BATCH)
    accum = BATCH // a.per_device_batch

    # Dynamic padding: the collator pads each micro-batch to its longest note and masks
    # padding in the labels, which gives the same loss as the published padding to 1024.
    def tokenize(ex):
        return tok(ex["text"], truncation=True, max_length=SEQ_LEN)

    tokenized = ds.map(tokenize, batched=True, remove_columns=["text"])

    dp = run.budget != "nodp"
    author_mapping = None
    if dp and run.unit == "author":
        author_mapping = create_author_mapping(tokenized["train"], "author")
    tokenized = tokenized.remove_columns(["author", "file"])
    n_units = len(author_mapping) if author_mapping is not None else n_train
    largest_unit = max(map(len, author_mapping)) if author_mapping is not None else 1
    canary_records = sum(a == data.CANARY_AUTHOR for a in train_authors)
    logger.info(f"{run.id}: {n_train} records, {n_units} privacy units "
                f"(largest {largest_unit}), canary records in train {canary_records}, steps {steps}")

    if os.environ.get("DPLEAK_FUSED_CE", "1") == "1":
        # Fused linear + cross-entropy (Liger): same loss, without materialising the
        # (batch x 1024 x 128k) fp32 logits; lets the runs fit on shared GPUs.
        from liger_kernel.transformers import apply_liger_kernel_to_llama
        apply_liger_kernel_to_llama(rope=False, rms_norm=False, swiglu=False, cross_entropy=False,
                                    fused_linear_cross_entropy=True)
    model = transformers.AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, torch_dtype=torch.bfloat16, quantization_config=bnb_config(), device_map={"": 0})
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=False)
    model = get_peft_model(model, LoraConfig(
        r=4, lora_alpha=32, lora_dropout=0.0,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"]))

    targs = dp_transformers.TrainingArguments(
        output_dir=str(out / "trainer"), per_device_train_batch_size=a.per_device_batch,
        gradient_accumulation_steps=accum, max_steps=steps, num_train_epochs=EPOCHS,
        learning_rate=3e-4, lr_scheduler_type="constant", weight_decay=0.01,
        max_grad_norm=(0.0 if dp else 1.0), seed=run.seed, data_seed=run.seed,
        logging_steps=5, save_strategy="no", eval_strategy="no", report_to=[],
        remove_unused_columns=False, dataloader_num_workers=2, disable_tqdm=True,
        bf16=False, log_level="info")
    collator = dp_transformers.DataCollatorForPrivateCausalLanguageModeling(tok)

    privacy = {}
    if dp:
        pargs = dp_transformers.PrivacyArguments(
            per_sample_max_grad_norm=1.0, target_epsilon=run.epsilon)
        trainer = OpacusDPTrainer(
            model=model, args=targs, train_dataset=tokenized["train"],
            privacy_args=pargs, author_mapping=author_mapping, data_collator=collator)
        privacy = dict(
            unit=run.unit, n_units=n_units, largest_unit_records=largest_unit,
            delta=pargs.target_delta, sampling_probability=trainer.sampling_probability,
            accounted_steps=trainer.num_steps, noise_multiplier=pargs.noise_multiplier,
            target_epsilon=run.epsilon)
        logger.info(f"privacy: {privacy}")
    else:
        trainer = transformers.Trainer(model=model, args=targs, train_dataset=tokenized["train"],
                                       data_collator=collator)

    if a.max_steps:   # smoke test: accounting above uses the full schedule
        trainer.args.max_steps = a.max_steps
    result = trainer.train()
    if dp:
        privacy["epsilon_prv"] = trainer.get_prv_epsilon()
        privacy["epsilon_rdp"] = trainer.get_rdp_epsilon()
        privacy["optimizer_steps"] = trainer.state.global_step

    m = model
    while hasattr(m, "_module"):      # GradSampleModule wrapper
        m = m._module
    m.save_pretrained(out)

    # utility proxy: mean NLL on a fixed subset of 200 original training notes
    import random
    originals = [i for i, f in enumerate(train_files) if not f.startswith("canary_")]
    sub = random.Random(0).sample(originals, 200)
    texts = [ds["train"][i]["text"] for i in sub]
    held = list(ds["test"]["text"])
    nll_train = mean_nll(m, tok, texts)
    nll_held = mean_nll(m, tok, held)
    losses = [h for h in trainer.state.log_history if "loss" in h]

    meta = dict(
        run=run.asdict(), base_model=BASE_MODEL, n_train_records=n_train,
        n_heldout_records=len(held), canary_records_in_train=canary_records,
        steps=trainer.state.global_step, per_device_batch=a.per_device_batch,
        grad_accum=accum, effective_batch=BATCH, seq_len=SEQ_LEN,
        privacy=privacy, train_loss_curve=[(h["step"], h["loss"]) for h in losses],
        final_train_loss_last50=(sum(h["loss"] for h in losses[-10:]) / max(1, len(losses[-10:]))),
        utility_nll_train200=nll_train, utility_ppl_train200=math.exp(nll_train),
        nll_heldout=nll_held, train_runtime_s=result.metrics.get("train_runtime"),
        wall_s=time.time() - t0, gpu=torch.cuda.get_device_name(0),
        versions=dict(torch=torch.__version__, transformers=transformers.__version__,
                      peft=__import__("peft").__version__, opacus=__import__("opacus").__version__),
        git=git_commit())
    (out / "run.json").write_text(json.dumps(meta, indent=1))
    logger.info(f"done {run.id} in {meta['wall_s']:.0f}s; privacy={privacy}")


if __name__ == "__main__":
    main()
