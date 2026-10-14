"""
Canary perplexity ranking for one fine-tuned adapter.

    python -m dpleak.score --run i2b2_docs100_A_eps8_author_s42 --runs-dir runs
    python -m dpleak.score --adapter /old/llama-1B-i2b2-10can-common-nodp --dataset i2b2 --out x.json

For every profile (Tagset A and B, the inserted one and the non-inserted control) and
tuple, the true sentence is ranked by perplexity among 10,000 alternatives built from
the same template. For single entities the alternatives are the full pool of 10,000
values of that type (canaries/candidate_pools); for multi-entity tuples they are 10,000
distinct random combinations of pool values, drawn with three seeds (0, 1, 2).
Perplexity is that of the sentence alone (BOS + sentence), as in the published runs.
rank = 1 + number of alternatives with strictly lower perplexity.
Sentence-canary runs are scored with the inserted sentences as templates.
"""
import argparse
import json
import os
import random
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
from . import spec  # noqa: E402

BASE_MODEL = os.environ.get("DPLEAK_BASE_MODEL", "meta-llama/Llama-3.2-1B")
N_CAND = 10000
CAND_SEEDS = (0, 1, 2)
POOL_KEY = {"name": "NAME", "phone": "PHONE", "email": "EMAIL", "address": "ADDRESS"}


def pools():
    d = REPO / "canaries" / "candidate_pools"
    return {lang: json.loads((d / f"10000_tags_{lang}.json").read_text(encoding="utf-8"))
            for lang in ("en", "es")}


def candidates(dataset, tagset, tup, template, seed, pool):
    """Index 0 = true sentence; 1..N_CAND alternatives."""
    truth = spec.PROFILES[(dataset, tagset)]
    fields = spec.TUPLES[tup]
    out = [template.format(**truth)]
    if len(fields) == 1:
        f = fields[0]
        vals = [v for v in pool[POOL_KEY[f]] if v != truth[f]][:N_CAND]
        out += [template.format(**{f: v}) for v in vals]
        return out
    rng = random.Random(f"{dataset}|{tagset}|{tup}|{seed}")
    seen = {tuple(truth[f] for f in fields)}
    while len(out) <= N_CAND:
        fill = tuple(rng.choice(pool[POOL_KEY[f]]) for f in fields)
        if fill in seen:
            continue
        seen.add(fill)
        out.append(template.format(**dict(zip(fields, fill))))
    return out


def load(adapter):
    import torch
    import transformers
    from peft import PeftModel
    q = transformers.BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_use_double_quant=True,
                                        bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16)
    base = transformers.AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, torch_dtype=torch.bfloat16, quantization_config=q, device_map={"": 0})
    model = PeftModel.from_pretrained(base, str(adapter)).eval() if adapter else base.eval()
    tok = transformers.AutoTokenizer.from_pretrained(BASE_MODEL)
    tok.pad_token = tok.pad_token or tok.eos_token
    tok.padding_side = "right"
    return model, tok


def nll(model, tok, texts, bs=128):
    """Per-sentence (mean NLL, summed NLL) over the tokens after BOS."""
    import torch
    means, sums = [], []
    for i in range(0, len(texts), bs):
        enc = tok(texts[i:i + bs], return_tensors="pt", padding=True).to(model.device)
        with torch.no_grad():
            logits = model(input_ids=enc.input_ids, attention_mask=enc.attention_mask).logits[:, :-1].float()
        tgt = enc.input_ids[:, 1:]
        m = enc.attention_mask[:, 1:].float()
        tok_nll = torch.nn.functional.cross_entropy(logits.transpose(1, 2), tgt, reduction="none") * m
        s = tok_nll.sum(1)
        sums += s.tolist()
        means += (s / m.sum(1)).tolist()
    return np.array(means), np.array(sums)


def rank_of(x):
    return int(1 + (x[1:] < x[0]).sum())


def score(model, tok, dataset, canary="docs", tagsets=spec.TAGSETS, save_arrays=None):
    lang = spec.LANG[dataset]
    pool = pools()[lang]
    templates = spec.DOC_TEMPLATES[lang] if canary == "docs" else spec.SENT_LINES[lang]
    res, arrays = {}, {}
    for tagset in tagsets:
        for tup, tmpl in templates.items():
            seeds = CAND_SEEDS if len(spec.TUPLES[tup]) > 1 else (0,)
            for seed in seeds:
                c = candidates(dataset, tagset, tup, tmpl, seed, pool)
                mean, tot = nll(model, tok, c)
                res.setdefault(tagset, {}).setdefault(tup, {})[str(seed)] = dict(
                    rank=rank_of(mean), rank_sum_nll=rank_of(tot),
                    ppl_true=float(np.exp(mean[0])), median_ppl=float(np.exp(np.median(mean))))
                arrays[f"{tagset}|{tup}|{seed}"] = mean.astype(np.float32)
    if save_arrays:
        np.savez_compressed(save_arrays, **arrays)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run")
    ap.add_argument("--runs-dir", default=str(REPO / "runs"))
    ap.add_argument("--adapter", help="score an arbitrary adapter dir (e.g. the legacy ones)")
    ap.add_argument("--dataset")
    ap.add_argument("--canary", default="docs")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.run:
        r = spec.parse_run_id(a.run)
        d = Path(a.runs_dir) / r.id
        model, tok = load(d)
        tagsets = spec.TAGSETS if r.canary == "docs" else ("A",)
        res = score(model, tok, r.dataset, r.canary, tagsets, save_arrays=d / "canary_nll.npz")
        out = dict(run=r.asdict(), inserted_tagset=r.tagset if r.exposure else None, ranks=res)
        (d / "ranks.json").write_text(json.dumps(out, indent=1))
    else:
        model, tok = load(a.adapter)
        tagsets = spec.TAGSETS if a.canary == "docs" else ("A",)
        res = score(model, tok, a.dataset, a.canary, tagsets)
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(dict(adapter=str(a.adapter), dataset=a.dataset,
                                               canary=a.canary, ranks=res), indent=1))
    print("scored", a.run or a.adapter, flush=True)


if __name__ == "__main__":
    main()
