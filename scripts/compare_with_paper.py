#!/usr/bin/env python3
"""
Consistency check: published numbers vs. (a) the published adapters re-scored with the
pinned canary values and (b) the re-run (median over training seeds, and seed 42 alone).

    python scripts/compare_with_paper.py --extract /path/to/published/main.tex   # once
    python scripts/compare_with_paper.py                                          # report

--extract parses the canary-rank, document-vs-sentence and leakage tables of the
previously submitted manuscript into legacy/paper_values.json.
The report (results/consistency_report.md) classifies every canary cell:
  BUG        cell of the 24 evaluated against the wrong profile (legacy/AUDIT.md)
  OK         same order of magnitude (|log10 ratio| <= 1) or both near chance (>= 2,000)
  DIFF       otherwise
"""
import argparse
import json
import math
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

PV = REPO / "legacy" / "paper_values.json"
RES = REPO / "results"
LABEL_TUPLE = {"N": "N", "P": "P", "E": "E", "A": "A", "N, A": "N,A", "N,A": "N,A",
               "N, A, E": "N,A,E", "N,A,E": "N,A,E", "N, A, P, E": "N,A,P,E", "N,A,P,E": "N,A,P,E",
               "Name (N)": "N", "Address (A)": "A", "Phone (P)": "P", "Email (E)": "E"}
BUDGET_COLS = ["nodp", "eps8", "eps4"]
LEGACY_BUDGET = {"nodp": "nodp", "eps8": "8eps", "eps4": "4eps"}
LEGACY_TAG = {"A": "common", "B": "rare"}


def table_block(tex, label):
    end = tex.index(f"\\label{{{label}}}")
    start = tex.rfind("\\begin{table", 0, end)
    return tex[start:end]


def num(x):
    return int(x.replace("{,}", "").replace(",", "").strip())


def parse_rank_table(block, exposure):
    out = {}
    ds = None
    for line in block.splitlines():
        if "i2b2" in line and "rotatebox" in line:
            ds = "i2b2"
        if "MEDDOCAN" in line and "rotatebox" in line:
            ds = "meddocan"
        cells = [c.strip() for c in line.replace("\\\\", "").split("&")]
        if ds and len(cells) == 8 and cells[1] in LABEL_TUPLE:
            tup = LABEL_TUPLE[cells[1]]
            vals = [num(c) for c in cells[2:]]
            for i, tag in enumerate(("A", "B")):
                for j, b in enumerate(BUDGET_COLS):
                    out[f"{ds}|{exposure}|{tag}|{b}|{tup}"] = vals[3 * i + j]
    return out


def parse_doc_sentence(block):
    out, ds = {}, None
    names = {"Name": "N", "Address": "A", "Phone": "P", "Email": "E"}
    for line in block.splitlines():
        if "textbf{i2b2" in line:
            ds = "i2b2"
        elif "textbf{MEDDOCAN" in line:
            ds = "meddocan"
        cells = [c.strip() for c in line.replace("\\\\", "").split("&")]
        if ds and len(cells) == 5 and cells[0] in names:
            for (canary, b), c in zip([("sent", "nodp"), ("sent", "eps8"), ("docs", "nodp"), ("docs", "eps8")],
                                      cells[1:]):
                r, p = c.split("/")
                out[f"{ds}|{canary}10|A|{b}|{names[cells[0]]}"] = dict(rank=num(r), ppl=float(p))
    return out


def parse_leakage(block):
    out, mode, ds = {}, "substring", None
    for line in block.splitlines():
        if "Whole-word" in line:
            mode = "whole_word"
        if "i2b2 2014" in line:
            ds = "i2b2"
        if "MEDDOCAN" in line and "multirow" in line:
            ds = "meddocan"
        cells = [c.strip() for c in line.replace("\\\\", "").split("&")]
        if ds and len(cells) == 7 and ("Non-DP" in cells[1] or "epsilon" in cells[1]):
            b = "nodp" if "Non-DP" in cells[1] else ("eps8" if "8" in cells[1] else "eps4")
            single = num(cells[2].split("(")[0])
            out[f"{ds}|{b}|{mode}"] = dict(singles=single, pairs=num(cells[3]), pairs_one_doc=num(cells[4]),
                                           triples=num(cells[5]), quadruples=num(cells[6]))
    return out


def extract(tex_path):
    tex = Path(tex_path).read_text()
    vals = {"canary_ranks": {}, "doc_vs_sentence": {}, "leakage": {}}
    for label, k in (("tab:tuple_ranks", 100), ("tab:sensitivity_expanded", 10), ("tab:rep1", 1)):
        vals["canary_ranks"].update(parse_rank_table(table_block(tex, label), k))
    vals["doc_vs_sentence"] = parse_doc_sentence(table_block(tex, "tab:document_sentence"))
    vals["leakage"] = parse_leakage(table_block(tex, "tab:pii_leakage"))
    PV.write_text(json.dumps(vals, indent=1))
    print(f"extracted {len(vals['canary_ranks'])} rank cells, {len(vals['doc_vs_sentence'])} doc/sentence "
          f"cells, {len(vals['leakage'])} leakage rows -> {PV}")


def classify(paper, new, bug=False):
    if bug:
        return "BUG"
    if new is None:
        return "pending"
    if paper >= 2000 and new >= 2000:
        return "OK"
    r = abs(math.log10(max(new, 1) / max(paper, 1)))
    return "OK" if r <= 1 else "DIFF"


def report():
    pv = json.loads(PV.read_text())
    audit = json.loads((REPO / "legacy" / "canary_eval_audit.json").read_text())
    legacy = json.loads((RES / "legacy_rescore.json").read_text()) if (RES / "legacy_rescore.json").exists() else {}
    cs = json.loads((RES / "canary_summary.json").read_text()) if (RES / "canary_summary.json").exists() else {}
    ranks = json.loads((RES / "canary_ranks.json").read_text()) if (RES / "canary_ranks.json").exists() else {}
    lines = ["# Consistency of the re-run with the previously submitted numbers", "",
             "Classes: OK (same order of magnitude, or both >= 2,000), DIFF, BUG (legacy cell scored against the "
             "wrong profile), pending (not yet computed).", "",
             "## Canary ranks", "",
             "| cell | paper | legacy re-score | class | new seed 42 | new median (seeds) | class |",
             "|---|---|---|---|---|---|---|"]
    counts = {"legacy": {}, "new": {}}
    for key, paper in sorted(pv["canary_ranks"].items()):
        ds, k, tag, b, tup = key.split("|")
        akey = f"{ds}|{tag}|{k}doc|{LEGACY_BUDGET[b]}|{tup}"
        bug = audit.get(akey, {}).get("status") == "WRONG_TRUTH"
        lname = f"llama-1B-{ds}-{k}can-{LEGACY_TAG[tag]}-{LEGACY_BUDGET[b]}"
        lv = legacy.get(lname, {}).get(tag, {}).get(tup, {}).get("0", {}).get("rank")
        setting = "nodp" if b == "nodp" else f"{b}_record"
        rid = f"{ds}_docs{k}_{tag}_{b}" + ("" if b == "nodp" else "_record") + "_s42"
        n42 = ranks.get(rid, {}).get("ranks", {}).get(tag, {}).get(tup, {}).get("0", {}).get("rank")
        nmed = (cs.get(f"{ds}|docs{k}|{tag}|{setting}|inserted", {}).get(tup, {}).get("rank") or {}).get("median")
        c1 = classify(paper, lv, bug)
        c2 = classify(paper, nmed if nmed is not None else n42, bug)
        counts["legacy"][c1] = counts["legacy"].get(c1, 0) + 1
        counts["new"][c2] = counts["new"].get(c2, 0) + 1
        f = lambda x: "--" if x is None else (f"{x:.0f}" if isinstance(x, (int, float)) else str(x))  # noqa: E731
        lines.append(f"| {key} | {paper} | {f(lv)} | {c1} | {f(n42)} | {f(nmed)} | {c2} |")
    lines[5:5] = [f"Summary: legacy re-score {counts['legacy']}; re-run {counts['new']}", ""]

    lines += ["", "## Leakage (unique counts; new = median over training seeds)", "",
              "| row | metric | paper | new | ratio |", "|---|---|---|---|---|"]
    ls = json.loads((RES / "leakage_summary.json").read_text()) if (RES / "leakage_summary.json").exists() else {}
    for key, pvals in sorted(pv["leakage"].items()):
        ds, b, mode = key.split("|")
        setting = "nodp" if b == "nodp" else f"{b}_record"
        new = ls.get(f"{ds}|{setting}", {}).get(mode, {})
        for m, p in pvals.items():
            n = (new.get(m) or {}).get("median")
            ratio = f"{n / p:.2f}" if n is not None and p else "--"
            lines.append(f"| {key} | {m} | {p} | {'--' if n is None else round(n)} | {ratio} |")
    (RES / "consistency_report.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:7]))
    print(f"-> {RES / 'consistency_report.md'}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--extract")
    a = ap.parse_args()
    if a.extract:
        extract(a.extract)
    else:
        report()
