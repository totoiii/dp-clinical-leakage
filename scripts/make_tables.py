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


def rank_of(cs, key, tup):
    """Rank summary over training seeds; for tuples, each seed's rank is the median over the
    three candidate draws (singles have a single, deterministic candidate set)."""
    e = cs.get(key, {}).get(tup, {})
    return e.get("rank_median_over_candidate_draws") or e.get("rank")


def redundant_author(ds, exposure, setting):
    """MEDDOCAN author-level runs with at most one canary document are not trained: every
    privacy unit then holds one note, so they coincide with the record-level runs."""
    return ds == "meddocan" and setting.endswith("_author") and exposure <= 1


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
                    cells.append("$=$" if redundant_author(ds, exposure, s) else cell(rank_of(cs, k, tup), rng))
            lines.append(f"{first} & {TUPLE_TEX[tup]} & " + " & ".join(cells) + " \\\\")
        if di == 0:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


DVS_SETS = ["nodp", "eps8_record", "eps8_author"]
ENTITY = {"N": "Name", "A": "Address", "P": "Phone", "E": "Email"}


def doc_vs_sentence(cs, exposure, nf=None):
    """Per-entity rank, sentence vs document canaries (Tagset A; non-DP, eps=8 record and
    author). MEDDOCAN adds the name ranked in the header-field format of the documents."""
    nf = nf or {}
    lines = ["\\begin{tabular}{l rrr rrr}", "\\toprule",
             "& \\multicolumn{3}{c}{\\textbf{Sentences}} & \\multicolumn{3}{c}{\\textbf{Documents}} \\\\",
             "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}",
             "& & \\multicolumn{2}{c}{$\\epsilon{=}8$} & & \\multicolumn{2}{c}{$\\epsilon{=}8$} \\\\",
             "\\cmidrule(lr){3-4}\\cmidrule(lr){6-7}",
             "\\textbf{Entity} & Non-DP & record & author & Non-DP & record & author \\\\", "\\midrule"]
    for ds in spec.DATASETS:
        lines.append(f"\\multicolumn{{7}}{{l}}{{\\textbf{{{DSNAME[ds]}}}}} \\\\")
        cols = {}
        for canary in ("sent", "docs"):
            for s in DVS_SETS:
                k = f"{ds}|{canary}{exposure}|A|{s}|inserted"
                cols[(canary, s)] = {t: (rank_of(cs, k, t) or {}).get("median") for t in ENTITY}
        for t, nm in ENTITY.items():
            lines.append(nm + " & " + " & ".join(fmt_int(cols[(c, s)][t]) for c in ("sent", "docs")
                                                 for s in DVS_SETS) + " \\\\")
            if t == "N" and ds == "meddocan" and nf:
                v = [(nf.get(f"{ds}|docs{exposure}|A|{s}|inserted", {}).get("rank") or {}).get("median")
                     for s in DVS_SETS]
                lines.append("\\quad as written$^{\\dagger}$ & -- & -- & -- & " + " & ".join(map(fmt_int, v)) + " \\\\")
        sd = []
        for c in ("sent", "docs"):
            for s in DVS_SETS:
                v = [x for x in cols[(c, s)].values() if x is not None]
                sd.append(f"\\textit{{{fmt_int(st.pstdev(v))}}}" if len(v) > 1 else "--")
        lines.append("\\textit{SD across entities} & " + " & ".join(sd) + " \\\\")
        lines.append("\\midrule")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def sentence_control_table(sc):
    """Sentence-canary templates scored on the no-canary models: median (min--max)."""
    lines = ["\\begin{tabular}{ll rrr}", "\\toprule",
             "& & & \\multicolumn{2}{c}{$\\epsilon{=}8$} \\\\", "\\cmidrule(lr){4-5}",
             "\\textbf{Data} & \\textbf{Entity} & Non-DP & record & author \\\\", "\\midrule"]
    for di, ds in enumerate(spec.DATASETS):
        for i, (t, nm) in enumerate(ENTITY.items()):
            first = f"\\multirow{{4}}{{*}}{{{DSNAME[ds]}}}" if i == 0 else ""
            cells = ["$=$" if redundant_author(ds, 0, s) else
                     stacked(sc.get(f"{ds}|sent_control|A|{s}|no_canary_model", {}).get(t))
                     for s in DVS_SETS]
            lines.append(f"{first} & {nm} & " + " & ".join(cells) + " \\\\")
        if di == 0:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


def name_field_table(nf, cs):
    """MEDDOCAN document canaries: name rank in header-field format, median (min--max) over
    seeds, with the contiguous-name rank of Tables 5, 7--9 below it."""
    lines = ["\\begin{tabular}{ll rrrrr}", "\\toprule",
             "& & & \\multicolumn{2}{c}{record} & \\multicolumn{2}{c}{author} \\\\",
             "\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}",
             "\\textbf{Exposure} & \\textbf{Tagset} & " + " & ".join(SETHEAD[s] for s in SETTINGS) + " \\\\",
             "\\midrule"]
    for k in (0, 1, 10, 100):
        role = "no_canary_model" if k == 0 else "inserted"
        for tag in spec.TAGSETS:
            key = lambda s: f"meddocan|docs{k}|{tag}|{s}|{role}"  # noqa: E731
            cells = []
            for s in SETTINGS:
                if redundant_author("meddocan", k, s):
                    cells.append("$=$")
                    continue
                c = (rank_of(cs, key(s), "N") or {}).get("median")
                cells.append(stacked(nf.get(key(s), {}).get("rank")).replace(
                    "\\end{tabular}", f"\\\\[-2pt]{{\\tiny\\textit{{{fmt_int(c)}}}}}\\end{{tabular}}"))
            lab = "0 (control)" if k == 0 else str(k)
            lines.append(f"{lab} & {tag} & " + " & ".join(cells) + " \\\\")
        if k != 100:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}"]
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


def prv_upper(p, eps_error=0.05):
    """PRV upper bound on epsilon at the tolerance used to choose sigma. (The trainer's own
    accountant reports the bound at eps_error=0.1, i.e. up to ~0.05 above the target.)"""
    from prv_accountant import Accountant
    acc = Accountant(noise_multiplier=p["noise_multiplier"], sampling_probability=p["sampling_probability"],
                     delta=p["delta"], max_compositions=p["accounted_steps"], eps_error=eps_error)
    return acc.compute_epsilon(p["accounted_steps"])[2]


def accounting(index):
    """sigma summary for Table hyperparams, the per-configuration appendix table and
    results/accounting.json (epsilon_prv_trainer is the value stored in run.json, which the
    trainer's accountant computes at eps_error=0.1; epsilon_prv is the bound at 0.05)."""
    rows = {}
    for rid, m in index.items():
        r = spec.parse_run_id(rid)
        if r.budget == "nodp":
            continue
        k = (r.dataset, r.canary, r.exposure, r.unit, r.budget)
        rows.setdefault(k, []).append(dict(m, run_id=rid))
    lines = ["\\begin{tabular}{llrlrrrrrr}", "\\toprule",
             "\\textbf{Data} & \\textbf{Exp.} & & \\textbf{Unit} & \\textbf{$N_u$} & \\textbf{$q$} & "
             "\\textbf{$\\sigma$} & \\textbf{$\\epsilon_{\\mathrm{PRV}}$} & \\textbf{$\\epsilon_{\\mathrm{RDP}}$} & "
             "\\textbf{PPL} \\\\", "\\midrule"]
    js = []
    order = lambda x: (x[0][0], x[0][1] != "docs", x[0][2], x[0][3] != "record", x[0][4] != "eps8")  # noqa: E731
    for (ds, canary, k, unit, b), ms in sorted(rows.items(), key=order):
        p = ms[0]["privacy"]
        ppl = st.median(m["utility_ppl_train200"] for m in ms)
        eprv = prv_upper(p)
        erdp = st.median(m["privacy"]["epsilon_rdp"] for m in ms)
        exp = str(k) if canary == "docs" else f"{k} (sent.)"
        lines.append(f"{DSNAME[ds]} & {exp} & {SETHEAD[b + '_record']} & {unit} & {fmt_int(p['n_units'])} & "
                     f"{p['sampling_probability']:.3f} & {p['noise_multiplier']:.2f} & {eprv:.2f} & {erdp:.2f} & "
                     f"{ppl:.2f} \\\\")
        js.append(dict(dataset=ds, canary=canary, exposure=k, unit=unit, target_epsilon=spec.BUDGETS[b],
                       runs=sorted(m["run_id"] for m in ms),
                       n_units=p["n_units"], delta=p["delta"], sampling_probability=p["sampling_probability"],
                       steps=p["accounted_steps"], noise_multiplier=p["noise_multiplier"],
                       epsilon_prv=round(eprv, 4), epsilon_prv_trainer=round(p["epsilon_prv"], 4),
                       epsilon_rdp=round(erdp, 4), utility_ppl_train200_median=round(ppl, 3)))
    lines += ["\\bottomrule", "\\end{tabular}"]
    (RES / "accounting.json").write_text(json.dumps(js, indent=1))

    def sig(ds, unit, b):
        ms = rows.get((ds, "docs", 0, unit, b))
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


def stacked(summ):
    """median over (min--max) in one cell, to keep the appendix tables within the page width."""
    if not summ:
        return "--"
    return (f"\\begin{{tabular}}[t]{{@{{}}r@{{}}}}{fmt_int(summ['median'])}\\\\[-2pt]"
            f"{{\\tiny({fmt_int(summ['min'])}--{fmt_int(summ['max'])})}}\\end{{tabular}}")


def canary_range_table(cs, exposure, tag):
    """Appendix: median (min--max) over training seeds, one tagset, five settings."""
    role = "no_canary_model" if exposure == 0 else "inserted"
    lines = ["\\begin{tabular}{ll rrrrr}", "\\toprule",
             "& & & \\multicolumn{2}{c}{record} & \\multicolumn{2}{c}{author} \\\\",
             "\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}",
             "\\textbf{Data} & \\textbf{Tuple} & " + " & ".join(SETHEAD[s] for s in SETTINGS) + " \\\\", "\\midrule"]
    for di, ds in enumerate(spec.DATASETS):
        for ti, tup in enumerate(TUPLES):
            first = (f"\\multirow{{7}}{{*}}{{\\rotatebox{{90}}{{\\textbf{{{DSNAME[ds]}}}}}}}" if ti == 0 else "")
            cells = ["$=$" if redundant_author(ds, exposure, s) else
                     stacked(rank_of(cs, rank_key(ds, exposure, tag, s, role), tup)) for s in SETTINGS]
            lines.append(f"{first} & {TUPLE_TEX[tup]} & " + " & ".join(cells) + " \\\\")
        if di == 0:
            lines.append("\\midrule")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


LEAK_ROWS = {"i2b2": ["nodp", "eps8_record", "eps4_record", "eps8_author", "eps4_author", "base"],
             "meddocan": ["nodp", "eps8_record", "eps4_record", "base"]}
LEAK_LABEL = {"nodp": "Non-DP", "eps8_record": "$\\epsilon{=}8$, record", "eps4_record": "$\\epsilon{=}4$, record",
              "eps8_author": "$\\epsilon{=}8$, author", "eps4_author": "$\\epsilon{=}4$, author",
              "base": "Base model (no FT)"}
LEAK_METRICS = ["singles", "pairs", "pairs_one_doc", "triples", "quadruples"]


def leakage_table(ls, rng=False):
    """Unique leaked items per synthetic corpus of 1,000 documents (median over training seeds,
    or min--max with rng=True); substring and whole-word blocks."""
    lines = ["\\begin{tabular}{llrrrrr}", "\\toprule",
             "\\textbf{Dataset} & \\textbf{Setting} & \\textbf{Single} & \\textbf{2-Tuple} & \\textbf{2-Tuple} & "
             "\\textbf{3-Tuple} & \\textbf{4-Tuple} \\\\",
             "& & & \\textit{(any doc.)} & \\textit{(one doc.)} & & \\\\", "\\midrule"]
    for bi, mode in enumerate(("substring", "whole_word")):
        lines.append(f"\\multicolumn{{7}}{{l}}{{\\textit{{{'Substring' if mode == 'substring' else 'Whole-word'} matching}}}} \\\\")
        for ds in spec.DATASETS:
            rows = [r for r in LEAK_ROWS[ds] if f"{ds}|{r}" in ls]
            for ri, r in enumerate(rows):
                m = ls[f"{ds}|{r}"][mode]
                first = f"\\multirow{{{len(rows)}}}{{*}}{{{DSNAME[ds]}}}" if ri == 0 else ""
                cells = []
                for k in LEAK_METRICS:
                    v = m[k]
                    if rng:
                        cells.append(f"{fmt_int(v['min'])}--{fmt_int(v['max'])}")
                    elif k == "singles":
                        cells.append(f"{fmt_int(v['median'])} ({m['singles_pct']['median']:.2f}\\%)")
                    else:
                        cells.append(fmt_int(v["median"]))
                lines.append(f"{first} & {LEAK_LABEL[r]} & " + " & ".join(cells) + " \\\\")
            lines.append("\\midrule")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def largest_tuple_table(ls, mode="substring"):
    lines = ["\\begin{tabular}{llrrrrr}", "\\toprule",
             "\\textbf{Dataset} & \\textbf{Setting} & \\textbf{Profiles} & \\textbf{=1} & \\textbf{=2} & "
             "\\textbf{=3} & \\textbf{=4} \\\\", "\\midrule"]
    for ds in spec.DATASETS:
        rows = [r for r in LEAK_ROWS[ds] if r != "base" and f"{ds}|{r}" in ls]
        for ri, r in enumerate(rows):
            m = ls[f"{ds}|{r}"][mode]
            first = f"\\multirow{{{len(rows)}}}{{*}}{{{DSNAME[ds]}}}" if ri == 0 else ""
            cells = [fmt_int(m["profiles_leaked"]["median"])] + [fmt_int(m["largest_group"][g]["median"]) for g in "1234"]
            lines.append(f"{first} & {LEAK_LABEL[r]} & " + " & ".join(cells) + " \\\\")
        lines.append("\\midrule")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines)


ENRICH_PAIRS = {
    "i2b2": [("AGE+DATE", "AGE, DATE"), ("DATE+LOCATION", "DATE, LOCATION"), ("AGE+LOCATION", "AGE, LOCATION"),
             ("LOCATION+NAME", "\\textbf{LOCATION, NAME}"), ("ID", "ID, {\\footnotesize(any)}")],
    "meddocan": [("EDAD_SUJETO_ASISTENCIA+FECHAS", "AGE, DATE"),
                 ("EDAD_SUJETO_ASISTENCIA+NOMBRE_SUJETO_ASISTENCIA", "AGE, NAME"),
                 ("FECHAS+TERRITORIO", "DATE, TERRITORY"),
                 ("NOMBRE_SUJETO_ASISTENCIA+TERRITORIO", "\\textbf{NAME, TERRITORY}"),
                 ("ID_TITULACION_PERSONAL_SANITARIO", "LICENCE NO., {\\footnotesize(any)}")]}
ENRICH_SETTINGS = ["nodp", "eps8_record", "eps4_record", "eps8_author", "eps4_author"]


def _enrich_cell(ls, ds, setting, key, mode, rng):
    if redundant_author(ds, 0, setting):
        return "$=$"
    e = (ls.get(f"{ds}|{setting}", {}).get(mode, {}).get("enrichment", {}).get("any_per_doc", {}))
    if "+" not in key:   # all pairs with this identifier type
        vals = [x for tp, v in e.items() if key in tp.split("+") for x in v["values"]]
        if not vals:
            return "--"
        return "$\\infty$" if all(v == float("inf") for v in vals) else f"{min(vals):.1f}--{max(vals):.1f}"
    v = e.get(key)
    if not v:
        return "--"
    f = lambda x: "$\\infty$" if x == float("inf") else f"{x:.1f}"  # noqa: E731
    return f"{f(v['min'])}--{f(v['max'])}" if rng else f(v["median"])


def enrichment_table(ls, mode="substring", rng=False):
    lines = ["\\begin{tabular}{llrrrrr}", "\\toprule",
             "& & & \\multicolumn{2}{c}{record} & \\multicolumn{2}{c}{author} \\\\",
             "\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}",
             "\\textbf{Dataset} & \\textbf{Type pair} & " + " & ".join(SETHEAD[s] for s in ENRICH_SETTINGS) + " \\\\",
             "\\midrule"]
    for ds in spec.DATASETS:
        pairs = ENRICH_PAIRS[ds]
        for pi, (key, label) in enumerate(pairs):
            first = f"\\multirow{{{len(pairs)}}}{{*}}{{{'i2b2' if ds == 'i2b2' else 'MEDDOCAN'}}}" if pi == 0 else ""
            cells = [_enrich_cell(ls, ds, s, key, mode, rng) for s in ENRICH_SETTINGS]
            lines.append(f"{first} & {label} & " + " & ".join(cells) + " \\\\")
        lines.append("\\midrule")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    return "\n".join(lines)


def context_table():
    """Similarity rank of the source note (results/context_{ds}_{setting}.json): median over
    the corpora of the three training seeds; null = median of the null means, interval = from
    the lowest to the highest bound of the three per-corpus 2.5--97.5 percentile intervals."""
    lines = ["\\begin{tabular}{llrrrrr}", "\\toprule",
             "& & & \\multicolumn{2}{c}{\\textbf{Rank 1}} & \\multicolumn{2}{c}{\\textbf{Median rank}} \\\\",
             "\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}",
             "\\textbf{Dataset} & \\textbf{Setting} & \\textbf{Pairs} & \\textbf{Source} & \\textbf{Null} & "
             "\\textbf{Source} & \\textbf{Null} \\\\", "\\midrule"]
    out = {}
    for ds in spec.DATASETS:
        rows = [r for r in LEAK_ROWS[ds] if r != "base" and (RES / f"context_{ds}_{r}.json").exists()]
        for ri, r in enumerate(rows):
            d = json.loads((RES / f"context_{ds}_{r}.json").read_text())
            alls = [v["all"] for v in d.values()]
            n_notes = next(iter(d.values()))["n_notes"]
            med = lambda k: st.median(a[k] for a in alls)  # noqa: E731
            lo = lambda k: min(a[k][0] for a in alls)  # noqa: E731
            hi = lambda k: max(a[k][1] for a in alls)  # noqa: E731
            row = dict(pairs=med("pairs"), rank1=med("rank1"), rank1_null=med("rank1_null_mean"),
                       rank1_null_95=[lo("rank1_null_95"), hi("rank1_null_95")], median_rank=med("median_rank"),
                       median_rank_null=med("median_rank_null_mean"),
                       median_rank_null_95=[lo("median_rank_null_95"), hi("median_rank_null_95")],
                       per_seed={k: v["all"] for k, v in d.items()})
            out[f"{ds}|{r}"] = row
            first = f"\\multirow{{{len(rows)}}}{{*}}{{{DSNAME[ds]} ({fmt_int(n_notes)} notes)}}" if ri == 0 else ""
            lines.append(f"{first} & {LEAK_LABEL[r]} & {fmt_int(row['pairs'])} & {fmt_int(row['rank1'])} & "
                         f"{row['rank1_null']:.1f} ({row['rank1_null_95'][0]:.0f}--{row['rank1_null_95'][1]:.0f}) & "
                         f"{fmt_int(row['median_rank'])} & {fmt_int(row['median_rank_null'])} "
                         f"({row['median_rank_null_95'][0]:.0f}--{row['median_rank_null_95'][1]:.0f}) \\\\")
        lines.append("\\midrule")
    lines[-1] = "\\bottomrule"
    lines.append("\\end{tabular}")
    (RES / "context_summary.json").write_text(json.dumps(out, indent=1))
    return "\n".join(lines)


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
        nf = load("name_field_ranks.json")
        for k in (10, 100):
            w(f"doc_vs_sentence_{k}", doc_vs_sentence(cs, k, nf))
        if nf:
            w("name_field", name_field_table(nf, cs))
        sc = load("sent_control_ranks.json")
        if sc:
            w("sentence_control", sentence_control_table(sc))
        for k in (0, 1, 10, 100):
            for tag in spec.TAGSETS:
                w(f"canary_ranks_{k}docs_{tag}_range", canary_range_table(cs, k, tag))
    ls = load("leakage_summary.json")
    if ls:
        w("leakage", leakage_table(ls))
        w("leakage_range", leakage_table(ls, rng=True))
        w("largest_tuple", largest_tuple_table(ls))
        w("enrichment", enrichment_table(ls))
        w("enrichment_range", enrichment_table(ls, rng=True))
    if list(RES.glob("context_*_*.json")):
        w("context_rank", context_table())
    print("tables written to", out)


if __name__ == "__main__":
    main()
