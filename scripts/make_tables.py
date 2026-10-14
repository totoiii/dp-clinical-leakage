#!/usr/bin/env python3
"""
Build every LaTeX table of the manuscript from results/*.json (and, for the corpus
counts in the volume table, from the training conditions themselves).

    python scripts/make_tables.py --out ../paper/tables

Cells are medians over the three training seeds; *_range tables give "median (min-max)".
"""
import argparse
import json
import statistics as st
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from dpleak import spec  # noqa: E402

RES = REPO / "results"
DSNAME = {"i2b2": "i2b2 2014", "meddocan": "MEDDOCAN"}
SETTINGS = ["nodp", "eps8_record", "eps4_record", "eps8_author", "eps4_author"]
SETHEAD = {"nodp": "Non-DP", "eps8_record": "$\\epsilon{=}8$", "eps4_record": "$\\epsilon{=}4$",
           "eps8_author": "$\\epsilon{=}8$", "eps4_author": "$\\epsilon{=}4$"}
TUPLES = ["N", "P", "E", "A", "N,A", "N,A,E", "N,A,P,E"]
TUPLE_TEX = {t: t.replace(",", ", ") for t in TUPLES}


def load(name):
    p = RES / name
    return json.loads(p.read_text()) if p.exists() else {}


def fmt_int(x):
    if x is None:
        return "--"
    x = int(round(x))
    return f"{x:,}".replace(",", "{,}")


def cell(summ, rng=False):
    if not summ:
        return "--"
    m = fmt_int(summ["median"])
    if rng and summ["n"] > 1:
        return f"{m} {{\\scriptsize({fmt_int(summ['min'])}--{fmt_int(summ['max'])})}}"
    return m


def rank_key(ds, exposure, tagset, setting, role, canary="docs"):
    return f"{ds}|{canary}{exposure}|{tagset}|{setting}|{role}"


def canary_table(cs, exposure, rng=False, role=None):
    """Rows: dataset x tuple. Columns: Tagset A, B x (non-DP, record e8/e4, author e8/e4)."""
    role = role or ("no_canary_model" if exposure == 0 else "inserted")
    lines = [
        "\\begin{tabular}{ll rrrrr rrrrr}", "\\toprule",
        "& & \\multicolumn{5}{c}{\\textbf{Tagset A}} & \\multicolumn{5}{c}{\\textbf{Tagset B}} \\\\",
        "\\cmidrule(lr){3-7}\\cmidrule(lr){8-12}",
        "& & & \\multicolumn{2}{c}{record} & \\multicolumn{2}{c}{author} & & "
        "\\multicolumn{2}{c}{record} & \\multicolumn{2}{c}{author} \\\\",
        "\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}\\cmidrule(lr){9-10}\\cmidrule(lr){11-12}",
        "\\textbf{Data} & \\textbf{Tuple} & " + " & ".join(SETHEAD[s] for s in SETTINGS * 2) + " \\\\",
        "\\midrule"]
    for di, ds in enumerate(spec.DATASETS):
        for ti, tup in enumerate(TUPLES):
            first = (f"\\multirow{{7}}{{*}}{{\\rotatebox{{90}}{{\\textbf{{{DSNAME[ds]}}}}}}}"
                     if ti == 0 else "")
            cells = []
            for tag in spec.TAGSETS:
                for s in SETTINGS:
                    k = rank_key(ds, exposure, tag, s, role)
                    cells.append(cell(cs.get(k, {}).get(tup, {}).get("rank"), rng))
            lines.append(f"{first} & {TUPLE_TEX[tup]} & " + " & ".join(cells) + " \\\\")
        if di == 0:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def doc_vs_sentence(cs, exposure):
    """Per-entity rank, sentence vs document canaries (Tagset A, non-DP and eps=8 record)."""
    sets = ["nodp", "eps8_record"]
    lines = ["\\begin{tabular}{l rr rr}", "\\toprule",
             "& \\multicolumn{2}{c}{\\textbf{Sentences}} & \\multicolumn{2}{c}{\\textbf{Documents}} \\\\",
             "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}",
             "\\textbf{Entity} & Non-DP & $\\epsilon{=}8$ & Non-DP & $\\epsilon{=}8$ \\\\", "\\midrule"]
    names = {"N": "Name", "A": "Address", "P": "Phone", "E": "Email"}
    for ds in spec.DATASETS:
        lines.append(f"\\multicolumn{{5}}{{l}}{{\\textbf{{{DSNAME[ds]}}}}} \\\\")
        cols = {}
        for canary in ("sent", "docs"):
            for s in sets:
                k = f"{ds}|{canary}{exposure}|A|{s}|inserted"
                cols[(canary, s)] = {t: (cs.get(k, {}).get(t, {}).get("rank") or {}).get("median")
                                     for t in names}
        for t, nm in names.items():
            lines.append(nm + " & " + " & ".join(fmt_int(cols[(c, s)][t]) for c in ("sent", "docs")
                                                 for s in sets) + " \\\\")
        sd = []
        for c in ("sent", "docs"):
            for s in sets:
                v = [x for x in cols[(c, s)].values() if x is not None]
                sd.append(f"\\textit{{{fmt_int(st.pstdev(v))}}}" if len(v) > 1 else "--")
        lines.append("\\textit{SD across entities} & " + " & ".join(sd) + " \\\\")
        lines.append("\\midrule")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def volume_table():
    from dpleak import data
    lines = ["\\begin{tabular}{lrrrrrr}", "\\toprule",
             "\\textbf{Exposure} & \\textbf{Canary docs} & \\textbf{$N$} & \\textbf{Canary share} & "
             "\\textbf{Profile notes} & \\textbf{$N_u$ record} & \\textbf{$N_u$ author} \\\\",
             "& \\textbf{(each once)} & & & \\textbf{in training} & & \\\\", "\\midrule"]
    out = {}
    for ds in spec.DATASETS:
        lines.append(f"\\multicolumn{{7}}{{l}}{{\\textit{{{DSNAME[ds]}}}}} \\\\")
        for k in (0, 1, 10, 100):
            sp = data.training_split(ds, "docs", k, "A" if k else None)
            tr = sp["train"]
            n = len(tr)
            held = sum(f.startswith("canary_") for f in tr["file"])
            nu = len(set(tr["author"]))
            out[f"{ds}|{k}"] = dict(N=n, canary_in_train=held, units_author=nu)
            share = f"{100 * held / n:.2f}\\%"
            lines.append(f"{k} document{'s' if k != 1 else ''} & {k} & {fmt_int(n)} & {share} & {held} & "
                         f"{fmt_int(n)} & {fmt_int(nu)} \\\\")
        lines.append("\\midrule")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    (RES / "canary_volume.json").write_text(json.dumps(out, indent=1))
    return "\n".join(lines)


def accounting(index):
    """sigma summary for Table hyperparams and the per-configuration appendix table."""
    rows = {}
    for rid, m in index.items():
        r = spec.parse_run_id(rid)
        if r.budget == "nodp" or r.canary != "docs":
            continue
        k = (r.dataset, r.exposure, r.unit, r.budget)
        rows.setdefault(k, []).append(m)
    lines = ["\\begin{tabular}{llrlrrrrrr}", "\\toprule",
             "\\textbf{Data} & \\textbf{Exp.} & & \\textbf{Unit} & \\textbf{$N_u$} & \\textbf{$q$} & "
             "\\textbf{$\\sigma$} & \\textbf{$\\epsilon_{\\mathrm{PRV}}$} & \\textbf{$\\epsilon_{\\mathrm{RDP}}$} & "
             "\\textbf{PPL} \\\\", "\\midrule"]
    for (ds, k, unit, b), ms in sorted(rows.items(), key=lambda x: (x[0][0], x[0][1], x[0][2] != "record", x[0][3] != "eps8")):
        p = ms[0]["privacy"]
        ppl = st.median(m["utility_ppl_train200"] for m in ms)
        eprv = st.median(m["privacy"]["epsilon_prv"] for m in ms)
        erdp = st.median(m["privacy"]["epsilon_rdp"] for m in ms)
        lines.append(f"{DSNAME[ds]} & {k} & {SETHEAD[b + '_record']} & {unit} & {fmt_int(p['n_units'])} & "
                     f"{p['sampling_probability']:.3f} & {p['noise_multiplier']:.2f} & {eprv:.2f} & {erdp:.2f} & "
                     f"{ppl:.2f} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]

    def sig(ds, unit, b):
        ms = rows.get((ds, 0, unit, b))
        return f"{ms[0]['privacy']['noise_multiplier']:.2f}" if ms else "--"
    summary = ("i2b2: " + f"{sig('i2b2', 'record', 'eps8')} / {sig('i2b2', 'record', 'eps4')} (record), "
               f"{sig('i2b2', 'author', 'eps8')} / {sig('i2b2', 'author', 'eps4')} (author); "
               "MEDDOCAN: " + f"{sig('meddocan', 'record', 'eps8')} / {sig('meddocan', 'record', 'eps4')}"
               " ($\\epsilon{=}8$ / $4$)")
    return "\n".join(lines), summary


def utility(index):
    """Median utility PPL (200 training notes) per dataset x setting, no-canary condition."""
    out = {}
    for rid, m in index.items():
        r = spec.parse_run_id(rid)
        if r.canary == "docs":
            key = f"{r.dataset}|{r.exposure}|{'nodp' if r.budget == 'nodp' else r.budget + '_' + r.unit}"
            out.setdefault(key, []).append(m["utility_ppl_train200"])
    return {k: dict(median=st.median(v), min=min(v), max=max(v), n=len(v)) for k, v in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO.parent / "paper" / "tables"))
    ap.add_argument("--no-data", action="store_true", help="skip tables that need the restricted corpora")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    cs = load("canary_summary.json")
    index = load("runs_index.json")
    w = lambda name, txt: (out / f"{name}.tex").write_text(txt + "\n")  # noqa: E731
    if not a.no_data:
        w("canary_volume", volume_table())
    if index:
        acc, sig = accounting(index)
        w("accounting", acc)
        w("sigma_summary", sig)
        (RES / "utility_summary.json").write_text(json.dumps(utility(index), indent=1))
    if cs:
        for k in (0, 1, 10, 100):
            w(f"canary_ranks_{k}docs", canary_table(cs, k))
            w(f"canary_ranks_{k}docs_range", canary_table(cs, k, rng=True))
        for k in (10, 100):
            w(f"doc_vs_sentence_{k}", doc_vs_sentence(cs, k))
    print("tables written to", out)


if __name__ == "__main__":
    main()
