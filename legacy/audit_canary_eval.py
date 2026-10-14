#!/usr/bin/env python3
"""
Audit of the historical canary PPL-rank evaluation.

For every (dataset, exposure, tagset, budget, tuple) it reads the stored
candidates_<tuple>.txt (line "0:" is the candidate the pipeline treated as the
TRUE canary) and checks that it contains the values actually inserted in the
canary XML documents. It also reports the rank of that candidate and the
0-canary control model (same tuple, no canary in training).

Usage (needs the legacy results/output folder, ~2 GB, NOT in the email zips):
    python legacy/audit_canary_eval.py --results /path/to/results/output \
        --out legacy/canary_eval_audit.json

A precomputed output is shipped in legacy/canary_eval_audit.json.
"""
import argparse
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dpleak.spec import PROFILES  # noqa: E402

TUPLES = {"N": "['name']", "P": "['phone']", "E": "['email']", "A": "['address']",
          "N,A": "['name', 'address']", "N,A,E": "['name', 'email', 'address']",
          "N,A,P,E": "['name', 'email', 'phone', 'address']"}


def inserted_values(ds, tag):
    return PROFILES[(ds, "A" if tag == "common" else "B")]

DATASETS = ("i2b2", "meddocan")
EXPOSURES = ("1", "10", "100")
TAGSETS = ("common", "rare")          # common = Tagset A, rare = Tagset B
BUDGETS = ("nodp", "8eps", "4eps")


def true_rank(result_json: Path) -> int:
    rows = json.loads(result_json.read_text())
    return next(i for i, r in enumerate(rows) if str(r["filename"]) == "0") + 1


def first_candidate(txt: Path) -> str:
    return txt.read_text(encoding="utf-8").splitlines()[0].split(": ", 1)[1]


def audit_cell(root: Path, ds, rep, tag, eps, tup):
    d = root / f"llama-1B-{ds}-{rep}can-{tag}-{eps}"
    txt, res = d / f"candidates_{tup}.txt", d / f"candidates_{tup}_result.json"
    if not txt.exists():
        return {"status": "missing"}
    cand = first_candidate(txt)
    expected = inserted_values(ds, tag)
    wrong = {k: v for k, v in expected.items() if k in tup and v not in cand}
    ctrl = root / f"llama-1B-{ds}-0can-common-{eps}" / f"candidates_{tup}_result.json"
    return {
        "status": "OK" if not wrong else "WRONG_TRUTH",
        "rank": true_rank(res),
        "control_0can_rank": true_rank(ctrl) if ctrl.exists() and tag == "common" else None,
        "evaluated_candidate": cand,
        "missing_inserted_values": wrong,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, type=Path)
    ap.add_argument("--out", default="legacy/canary_eval_audit.json", type=Path)
    a = ap.parse_args()
    out, bad = {}, 0
    for ds in DATASETS:
        for rep in EXPOSURES:
            for tag in TAGSETS:
                for eps in BUDGETS:
                    for short, tup in TUPLES.items():
                        key = f"{ds}|{'A' if tag == 'common' else 'B'}|{rep}doc|{eps}|{short}"
                        out[key] = audit_cell(a.results, ds, rep, tag, eps, tup)
                        if out[key]["status"] != "OK":
                            bad += 1
                            print(f"{key:40} {out[key]['status']:12} "
                                  f"{out[key].get('missing_inserted_values')}")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"\n{bad} problematic cells of {len(out)}; written to {a.out}")


if __name__ == "__main__":
    main()
