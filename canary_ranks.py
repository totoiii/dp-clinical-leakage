#!/usr/bin/env python3
"""
Extract canary PPL ranks (incl. the previously unreported rep=1 condition)
and bootstrap confidence intervals for each rank.

Rank = position (1-indexed) of the true canary (filename == 0) among the
10,000 candidates sorted by ascending perplexity.

Bootstrap CI: resample the 10,000 candidate PPLs with replacement B times;
each resample recomputes the rank of the true canary's PPL among the sample.
Reports median rank and 95% percentile interval -> quantifies candidate-
sampling noise WITHOUT retraining (R2.7).
"""
import os
import json
import random

REPO = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(REPO, "results", "output")

# paper tuple label -> candidate filename tag
TUPLES = {
    "N": "['name']",
    "P": "['phone']",
    "E": "['email']",
    "A": "['address']",
    "N,A": "['name', 'address']",
    "N,A,E": "['name', 'email', 'address']",
    "N,A,P,E": "['name', 'email', 'phone', 'address']",
}
DATASETS = ["i2b2", "meddocan"]
REPS = ["1", "10", "100"]
TAGSETS = {"A": "common", "B": "rare"}   # relabelled; no 'common/rare' claim
EPS = {"nodp": "nodp", "8": "8eps", "4": "4eps"}
B = 2000  # bootstrap resamples


def load_ppls_and_rank(path):
    """Return (list of candidate ppls, true-canary ppl, rank)."""
    with open(path) as f:
        data = json.load(f)  # sorted ascending by ppl
    ppls = [d["ppl"] for d in data]
    true_ppl = None
    rank = None
    for i, d in enumerate(data):
        if str(d["filename"]) == "0":
            true_ppl = d["ppl"]
            rank = i + 1
            break
    return ppls, true_ppl, rank


def bootstrap_ci(ppls, true_ppl, b=B):
    """Analytic bootstrap: #candidates below true_ppl in a size-n resample
    (with replacement) is Binomial(n, k/n), k = observed # below.
    Normal approximation gives an instant 95% CI on the rank."""
    import math
    n = len(ppls)
    k = sum(1 for p in ppls if p < true_ppl)   # rank-1
    p = k / n
    sd = math.sqrt(n * p * (1 - p))
    lo = max(1, int(round(k - 1.96 * sd)) + 1)
    hi = min(n, int(round(k + 1.96 * sd)) + 1)
    med = k + 1
    return med, lo, hi


def main():
    random.seed(42)
    results = {}
    for ds in DATASETS:
        for tagset_label, tagset_code in TAGSETS.items():
            for rep in REPS:
                for eps_label, eps_code in EPS.items():
                    cfg = f"llama-1B-{ds}-{rep}can-{tagset_code}-{eps_code}"
                    cdir = os.path.join(OUT, cfg)
                    if not os.path.isdir(cdir):
                        continue
                    for tup_label, tag in TUPLES.items():
                        fp = os.path.join(cdir, f"candidates_{tag}_result.json")
                        if not os.path.isfile(fp):
                            continue
                        try:
                            ppls, true_ppl, rank = load_ppls_and_rank(fp)
                            if true_ppl is None:
                                continue
                            med, lo, hi = bootstrap_ci(ppls, true_ppl)
                            key = f"{ds}|Tagset{tagset_label}|rep{rep}|eps{eps_label}|{tup_label}"
                            results[key] = {
                                "rank": rank,
                                "boot_median": med,
                                "boot_ci95": [lo, hi],
                                "n_candidates": len(ppls),
                            }
                        except Exception as e:
                            print("ERR", cfg, tag, e)
    with open(os.path.join(REPO, "canary_ranks_bootstrap.json"), "w") as f:
        json.dump(results, f, indent=2)

    # Print a compact rep=1 table (the newly reported condition)
    print("\n=== NEW rep=1 condition (rank [95% CI]) ===")
    for ds in DATASETS:
        for ts in ["A", "B"]:
            print(f"\n-- {ds}  Tagset {ts}  (rep=1) --")
            for tup in TUPLES:
                cells = []
                for eps_label in ["nodp", "8", "4"]:
                    k = f"{ds}|Tagset{ts}|rep1|eps{eps_label}|{tup}"
                    if k in results:
                        r = results[k]
                        cells.append(f"{eps_label}:{r['rank']} [{r['boot_ci95'][0]}-{r['boot_ci95'][1]}]")
                    else:
                        cells.append(f"{eps_label}:--")
                print(f"   {tup:<10} " + "  ".join(cells))
    print(f"\nWrote canary_ranks_bootstrap.json ({len(results)} entries)")


if __name__ == "__main__":
    main()
