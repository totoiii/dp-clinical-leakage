"""
Generate the synthetic corpus of one model (exactly 1,000 non-empty documents).

    python -m dpleak.generate --run i2b2_docs0_eps8_record_s42      # fine-tuned model, seed 1
    python -m dpleak.generate --base i2b2 --gen-seed 2               # non-fine-tuned baseline

Same fixed prompt as training; top-k 50, nucleus p=0.95, temperature 1.0, no
repetition penalty, up to 512 new tokens, 4-bit nf4 base as in training. Empty
generations are discarded and sampling continues until 1,000 documents exist.
Output: generations.csv (sequence) in the run directory, or runs/base/{dataset}_g{seed}/.
These files reproduce training PII and must never leave the server.
"""
import argparse
import csv
import json
import time
from pathlib import Path

from . import data, spec
from .score import load

REPO = Path(__file__).resolve().parent.parent
N_DOCS = 1000


def generate(model, tok, dataset, seed, n=N_DOCS, batch=50):
    import torch
    import transformers
    transformers.set_seed(seed)
    p = data.prompt(dataset)
    ids = tok(p, return_tensors="pt").input_ids.to(model.device)
    docs, n_empty = [], 0
    while len(docs) < n:
        x = ids.repeat(batch, 1)
        with torch.no_grad():
            out = model.generate(input_ids=x, attention_mask=torch.ones_like(x), do_sample=True,
                                 temperature=1.0, top_k=50, top_p=0.95, repetition_penalty=1.0,
                                 max_new_tokens=512, pad_token_id=tok.pad_token_id)
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
    a = ap.parse_args()
    t0 = time.time()
    if a.run:
        r = spec.parse_run_id(a.run)
        d, ds, adapter = Path(a.runs_dir) / r.id, r.dataset, Path(a.runs_dir) / r.id
    else:
        ds = a.base
        d, adapter = Path(a.runs_dir) / "base" / f"{ds}_g{a.gen_seed}", None
    d.mkdir(parents=True, exist_ok=True)
    model, tok = load(adapter)
    docs, n_empty = generate(model, tok, ds, a.gen_seed)
    with open(d / "generations.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sequence"])
        w.writerows([s] for s in docs)
    (d / "generation.json").write_text(json.dumps(dict(
        dataset=ds, gen_seed=a.gen_seed, n_docs=len(docs), n_empty_discarded=n_empty,
        seconds=time.time() - t0, adapter=str(adapter) if adapter else None), indent=1))
    print("generated", d, len(docs), flush=True)


if __name__ == "__main__":
    main()
