"""
Generate the synthetic corpus of one model (exactly 1,000 non-empty documents).

    python -m dpleak.generate --run i2b2_docs0_eps8_record_s42      # fine-tuned model, seed 1
    python -m dpleak.generate --base i2b2 --gen-seed 2               # non-fine-tuned baseline

Same configuration as the published runs (legacy/generate_text.py): the base model in
full precision with the LoRA adapter applied, the fixed training prompt, top-k 50,
nucleus p=0.95, temperature 1.0, no repetition penalty, max_length 512 tokens including
the prompt. Empty generations are discarded and sampling continues until exactly 1,000
documents exist (the published runs kept 994-1,000). --quantized generates with the 4-bit
NF4 base used in training and 512 new tokens instead (see legacy/AUDIT.md, section 5), into
the run's nf4_generation/ subdirectory.
Output: generations.csv (sequence) in the run directory, or runs/base/{dataset}_g{seed}/.
These files reproduce training PII and must never leave the server.
"""
import argparse
import csv
import json
import time
from pathlib import Path

from . import data, spec
from .score import BASE_MODEL, load

REPO = Path(__file__).resolve().parent.parent
N_DOCS = 1000


def load_full_precision(adapter):
    """Full-precision base + adapter, as in legacy/generate_text.py."""
    import torch
    import transformers
    from peft import PeftModel
    model = transformers.AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float32)
    if adapter:
        model = PeftModel.from_pretrained(model, str(adapter))
    tok = transformers.AutoTokenizer.from_pretrained(BASE_MODEL)
    tok.pad_token = tok.pad_token or tok.eos_token
    return model.to("cuda").eval(), tok


def generate(model, tok, dataset, seed, n=N_DOCS, batch=50, max_length=512, max_new_tokens=None):
    import torch
    import transformers
    transformers.set_seed(seed)
    p = data.prompt(dataset)
    ids = tok(p, return_tensors="pt").input_ids.to(model.device)
    docs, n_empty = [], 0
    while len(docs) < n:
        x = ids.repeat(batch, 1)
        length = dict(max_new_tokens=max_new_tokens) if max_new_tokens else dict(max_length=max_length)
        with torch.no_grad():
            out = model.generate(input_ids=x, attention_mask=torch.ones_like(x), do_sample=True,
                                 temperature=1.0, top_k=50, top_p=0.95, repetition_penalty=1.0,
                                 pad_token_id=tok.pad_token_id, **length)
        for s in tok.batch_decode(out[:, ids.shape[1]:], skip_special_tokens=True,
                                  clean_up_tokenization_spaces=True):
            s = s.strip()
            if s:
                docs.append(s)
            else:
                n_empty += 1
    return docs[:n], n_empty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--base", help="dataset name: generate with the non-fine-tuned model")
    ap.add_argument("--gen-seed", type=int, default=1)
    ap.add_argument("--runs-dir", default=str(REPO / "runs"))
    ap.add_argument("--quantized", action="store_true", help="4-bit NF4 base as in training")
    a = ap.parse_args()
    t0 = time.time()
    if a.run:
        r = spec.parse_run_id(a.run)
        d, ds, adapter = Path(a.runs_dir) / r.id, r.dataset, Path(a.runs_dir) / r.id
    else:
        ds = a.base
        d, adapter = Path(a.runs_dir) / "base" / f"{ds}_g{a.gen_seed}", None
    if a.quantized:
        d = d / "nf4_generation"
    d.mkdir(parents=True, exist_ok=True)
    model, tok = load(adapter) if a.quantized else load_full_precision(adapter)
    docs, n_empty = generate(model, tok, ds, a.gen_seed, max_new_tokens=512 if a.quantized else None)
    with open(d / "generations.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sequence"])
        w.writerows([s] for s in docs)
    (d / "generation.json").write_text(json.dumps(dict(
        dataset=ds, gen_seed=a.gen_seed, n_docs=len(docs), n_empty_discarded=n_empty,
        seconds=time.time() - t0, adapter=str(adapter) if adapter else None,
        base_precision="nf4" if a.quantized else "fp32",
        max_new_tokens=512 if a.quantized else None,
        max_length_incl_prompt=None if a.quantized else 512), indent=1))
    print("generated", d, len(docs), flush=True)


if __name__ == "__main__":
    main()
