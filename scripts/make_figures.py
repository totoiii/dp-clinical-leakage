#!/usr/bin/env python3
"""
Figures of the manuscript from results/*.json (same summaries as make_tables.py).

    python scripts/make_figures.py --out ../paper/figures

canary_exposure_<tuple>.pdf: rank of the inserted profile against exposure (0 = no-canary
model), one panel per dataset x tagset, one series per privacy setting (median over training
seeds of the per-seed median over the three candidate draws, as in the tables; bars = min-max
over seeds). Log scale, rank 1 at the top, dotted line = chance (5,000).
single_top_leakage.pdf / combined_top_leakage.pdf: unique leaked training values per PII
type, and leaked type-distinct pairs per type pair, in the 1,000 documents of each model
(substring matching, median over training seeds), from results/leakage_runs.json.
enrichment.pdf: generative-null enrichment E per type pair and setting (median and min-max
over training seeds), from results/leakage_summary.json.
largest_tuple.pdf: profiles by the size of their largest type-distinct tuple co-occurring in
one synthetic document (median over training seeds), from results/leakage_summary.json.
"""
import argparse
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.colors  # noqa: E402
import matplotlib.ticker  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from dpleak import spec  # noqa: E402
from make_tables import ENRICH_PAIRS, rank_of, redundant_author  # noqa: E402

WIDTH = 5.1  # inches: the text width of the manuscript, so fonts print at their nominal size
STYLE = {  # colour-blind-safe (Okabe-Ito); record = solid / filled, author = dashed / open
    "nodp": dict(color="#000000", ls="-", marker="o", mfc="#000000", label="Non-DP"),
    "eps8_record": dict(color="#0072B2", ls="-", marker="s", mfc="#0072B2", label="ε=8, record"),
    "eps4_record": dict(color="#56B4E9", ls="-", marker="^", mfc="#56B4E9", label="ε=4, record"),
    "eps8_author": dict(color="#D55E00", ls="--", marker="s", mfc="white", label="ε=8, author"),
    "eps4_author": dict(color="#E69F00", ls="--", marker="^", mfc="white", label="ε=4, author"),
}
SETTINGS = list(STYLE)
DSNAME = {"i2b2": "i2b2 2014", "meddocan": "MEDDOCAN"}
EXPOSURES = (0, 1, 10, 100)
INK, GRID = "#333333", "#d9d9d9"


def setup():
    plt.rcParams.update({
        "font.family": "DejaVu Sans", "font.size": 7.5, "axes.titlesize": 7.5, "axes.labelsize": 7.5,
        "xtick.labelsize": 7, "ytick.labelsize": 7, "legend.fontsize": 7, "axes.linewidth": 0.6,
        "axes.edgecolor": INK, "xtick.color": INK, "ytick.color": INK, "axes.labelcolor": INK,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42, "savefig.dpi": 300})


def save(fig, out, name):
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(out / f"{name}.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print("wrote", out / f"{name}.pdf")


def tint(color, a=0.3):
    """The colour mixed with white (fill of the author-level bars)."""
    rgb = matplotlib.colors.to_rgb(color)
    return tuple(1 - a * (1 - x) for x in rgb)


def setting_legend(fig, settings=SETTINGS, kind="line"):
    if kind == "line":
        h = [Line2D([], [], color=STYLE[s]["color"], ls=STYLE[s]["ls"], marker=STYLE[s]["marker"],
                    mfc=STYLE[s]["mfc"], mec=STYLE[s]["color"], ms=4.5, lw=1.2) for s in settings]
    else:
        h = [Patch(facecolor=tint(STYLE[s]["color"]) if s.endswith("author") else STYLE[s]["color"],
                   edgecolor=STYLE[s]["color"], lw=1.0) for s in settings]
    fig.legend(h, [STYLE[s]["label"] for s in settings], loc="outside upper center", ncol=len(settings),
               frameon=False, handlelength=2.4, columnspacing=1.4)


# ---------------------------------------------------------------- canary rank vs exposure
def series(cs, ds, tag, setting, tup):
    """(x, median, low error, high error) per exposure; exposure 0 = the no-canary model."""
    xs, med, lo, hi = [], [], [], []
    for i, k in enumerate(EXPOSURES):
        if k and redundant_author(ds, k, setting):
            continue
        role = "no_canary_model" if k == 0 else "inserted"
        e = rank_of(cs, f"{ds}|docs{k}|{tag}|{setting}|{role}", tup)
        if e:
            xs.append(i)
            med.append(e["median"])
            lo.append(e["median"] - e["min"])
            hi.append(e["max"] - e["median"])
    return xs, med, lo, hi


def canary_exposure(cs, tup, out):
    fig, axes = plt.subplots(2, 2, figsize=(WIDTH, 4.2), sharex=True, sharey=True, layout="constrained")
    for r, ds in enumerate(spec.DATASETS):
        for c, tag in enumerate(spec.TAGSETS):
            ax = axes[r, c]
            for x in (0.5, 1.5, 2.5):
                ax.axvline(x, color=GRID, lw=0.5, zorder=0)
            ax.axhline(5000, color="#888888", lw=0.7, ls=":", zorder=0)
            for j, s in enumerate(SETTINGS):
                xs, med, lo, hi = series(cs, ds, tag, s, tup)
                if not xs:
                    continue
                sty = STYLE[s]
                off = (j - 2) * 0.085
                ax.errorbar([x + off for x in xs], med, yerr=[lo, hi], color=sty["color"], ls=sty["ls"], lw=1.1,
                            marker=sty["marker"], ms=4.2, mfc=sty["mfc"], mec=sty["color"], mew=0.9,
                            elinewidth=0.7, capsize=0, zorder=3 if s == "nodp" else 2)
            ax.set_yscale("log")
            ax.set_ylim(14000, 0.75)
            ax.yaxis.set_major_locator(matplotlib.ticker.FixedLocator([1, 10, 100, 1000, 10000]))
            ax.yaxis.set_minor_locator(matplotlib.ticker.NullLocator())
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
            ax.set_xlim(-0.45, 3.45)
            ax.set_xticks(range(len(EXPOSURES)), ["0\n(no canary)", "1", "10", "100"])
            ax.grid(axis="y", color=GRID, lw=0.5)
            ax.set_axisbelow(True)
            ax.set_title(f"{DSNAME[ds]}, Tagset {tag}", fontweight="bold", pad=4)
            ax.text(3.42, 5000 * 1.12, "chance", ha="right", va="top", fontsize=6, color="#777777")
        axes[r, 0].set_ylabel(f"rank of ({tup.replace(',', ', ')}), log scale\n(more memorized →)")
    fig.supxlabel("canary documents of the profile in training", fontsize=7.5)
    setting_legend(fig)
    save(fig, out, "canary_exposure_" + tup.replace(",", ""))


# ---------------------------------------------------------------- leakage by PII type
TYPE_EN = {"EDAD_SUJETO_ASISTENCIA": "AGE", "FECHAS": "DATE", "TERRITORIO": "TERRITORY", "PAIS": "COUNTRY",
           "NOMBRE_SUJETO_ASISTENCIA": "NAME", "NOMBRE_PERSONAL_SANITARIO": "CLINICIAN NAME", "CALLE": "STREET",
           "HOSPITAL": "HOSPITAL", "INSTITUCION": "INSTITUTION", "ID_SUJETO_ASISTENCIA": "PATIENT ID",
           "ID_TITULACION_PERSONAL_SANITARIO": "LICENSE NO.", "ID_CONTACTO_ASISTENCIAL": "CONTACT ID",
           "PROFESION": "PROFESSION", "FAMILIARES_SUJETO_ASISTENCIA": "RELATIVES", "OTROS_SUJETO_ASISTENCIA": "OTHER",
           "SEXO_SUJETO_ASISTENCIA": "SEX", "CORREO_ELECTRONICO": "EMAIL", "NUMERO_TELEFONO": "PHONE",
           "NUMERO_FAX": "FAX", "ID_ASEGURAMIENTO": "INSURANCE ID", "ID_EMPLEO_PERSONAL_SANITARIO": "EMPLOYEE ID",
           "CENTRO_SALUD": "HEALTH CENTRE", "URL_WEB": "URL", "IDENTIF_DISPOSITIVOS_NRSERIE": "DEVICE ID",
           "OTRO_NUMERO_IDENTIF": "OTHER ID", "IDENTIF_VEHICULOS_NRSERIE_PLACAS": "VEHICLE ID",
           "DIREC_PROT_INTERNET": "IP", "IDENTIF_BIOMETRICOS": "BIOMETRIC", "NUMERO_BENEF_PLAN_SALUD": "PLAN NO.",
           "ID_TITULACION": "LICENSE NO."}


def leak_counts(leak, ds, field, mode="substring"):
    """{setting: {label: median count over training seeds}} for field singles_by_type or pairs_by_typepair."""
    out = {}
    for s in SETTINGS:
        runs = [v for k, v in leak.items() if k.startswith(f"{ds}_docs0_") and
                (("nodp" in k) if s == "nodp" else (f"_{s}_" in k))]
        if not runs:
            continue
        acc = defaultdict(list)
        for v in runs:
            for t, c in v[mode][field].items():
                acc[" + ".join(TYPE_EN.get(x, x) for x in t.split("+"))].append(c)
        out[s] = {t: st.median(c + [0] * (len(runs) - len(c))) for t, c in acc.items()}
    return out


def leakage_bars(leak, field, name, top, out, xlabel):
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3.0), layout="constrained")
    for ax, ds in zip(axes, spec.DATASETS):
        c = leak_counts(leak, ds, field)
        labels = sorted(c["nodp"], key=lambda t: -c["nodp"][t])[:top]
        sets = [s for s in SETTINGS if s in c]
        h = 0.84 / len(sets)
        for i, s in enumerate(sets):   # first setting at the top of each group, as in the legend
            ys = [j + (i - (len(sets) - 1) / 2) * h for j in range(len(labels))]
            sty = STYLE[s]
            author = s.endswith("author")
            ax.barh(ys, [c[s].get(t, 0) for t in labels], height=h * 0.92, color=tint(sty["color"]) if author
                    else sty["color"], edgecolor=sty["color"], lw=0.8 if author else 0)
        ax.set_yticks(range(len(labels)), [t.replace(" + ", " +\n") if len(t) > 16 else t for t in labels],
                      fontsize=6.5)
        ax.set_ylim(len(labels) - 0.5, -0.5)
        ax.set_title(DSNAME[ds], fontweight="bold", pad=4)
        ax.grid(axis="x", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    fig.supxlabel(xlabel, fontsize=7.5)
    setting_legend(fig, kind="patch")
    save(fig, out, name)


# ---------------------------------------------------------------- enrichment
ENRICH_LABEL = {"AGE+DATE": "AGE, DATE", "DATE+LOCATION": "DATE, LOCATION", "AGE+LOCATION": "AGE, LOCATION",
                "LOCATION+NAME": "LOCATION, NAME", "ID": "ID, any",
                "EDAD_SUJETO_ASISTENCIA+FECHAS": "AGE, DATE",
                "EDAD_SUJETO_ASISTENCIA+NOMBRE_SUJETO_ASISTENCIA": "AGE, NAME",
                "FECHAS+TERRITORIO": "DATE, TERRITORY", "NOMBRE_SUJETO_ASISTENCIA+TERRITORIO": "NAME, TERRITORY",
                "ID_TITULACION_PERSONAL_SANITARIO": "LICENSE NO., any"}
INF_X = 330.0   # where E = infinity is drawn, right of the finite axis


def enrich_value(ls, ds, setting, key, mode="substring"):
    """(median, min, max) of E over training seeds, as in make_tables.enrichment_table;
    an identifier type alone ("ID") stands for all pairs containing it (infinite if all are)."""
    if redundant_author(ds, 0, setting):
        return None
    e = ls.get(f"{ds}|{setting}", {}).get(mode, {}).get("enrichment", {}).get("any_per_doc", {})
    if "+" not in key:
        vals = [x for tp, v in e.items() if key in tp.split("+") for x in v["values"]]
        inf = float("inf")
        return (inf, inf, inf) if vals and all(v == inf for v in vals) else None
    v = e.get(key)
    return (v["median"], v["min"], v["max"]) if v else None


def enrichment(ls, out):
    fig, axes = plt.subplots(1, 2, figsize=(WIDTH, 3.05), sharex=True, layout="constrained")
    for ax, ds in zip(axes, spec.DATASETS):
        pairs = [k for k, _ in ENRICH_PAIRS[ds]]
        sets = [s for s in SETTINGS if not redundant_author(ds, 0, s)]
        ticks = []
        for pi, key in enumerate(pairs):
            ticks.append(pi)
            if pi % 2 == 0:
                ax.axhspan(pi - 0.5, pi + 0.5, color="#f2f2f2", lw=0, zorder=0)
            for j, s in enumerate(sets):
                v = enrich_value(ls, ds, s, key)
                if v is None:
                    continue
                y = pi + (j - (len(sets) - 1) / 2) * 0.19
                sty = STYLE[s]
                med, lo, hi = (INF_X if x == float("inf") else x for x in v)
                ax.plot([lo, hi], [y, y], color=sty["color"], lw=1.0, solid_capstyle="butt", zorder=2)
                ax.plot(med, y, marker=sty["marker"], ms=4.2, color=sty["color"], mfc=sty["mfc"], mew=0.9,
                        ls="none", zorder=3)
                if med != INF_X:
                    ax.annotate(f"{v[0]:.1f}", (hi, y), xytext=(5, 0), textcoords="offset points", va="center", ha="left",
                                fontsize=5.6, color=sty["color"])
        ax.set_xscale("log")
        ax.set_xlim(0.8, INF_X * 1.6)
        ax.axvline(1, color="#888888", lw=0.7, ls=":")
        ax.axvspan(190, INF_X * 1.6, color="#fbe9e7", lw=0, zorder=0)
        ax.set_xticks([1, 10, 100, INF_X], ["1", "10", "100", "∞"])
        ax.xaxis.set_minor_locator(matplotlib.ticker.LogLocator(subs=range(2, 10)))
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
        ax.set_yticks(ticks, [ENRICH_LABEL[k] for k in pairs], fontsize=6.8)
        ax.set_ylim(len(pairs) - 0.5, -0.5)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
        ax.set_title(DSNAME[ds], fontweight="bold", pad=4)
        ax.grid(axis="x", color=GRID, lw=0.5, which="major")
        ax.set_axisbelow(True)
        ax.text(1.08, len(pairs) - 0.55, "E = 1:\nbase-model\nrate", fontsize=5.5, color="#777777", va="bottom")
        ax.text(INF_X, -0.47, "never in\nbase model", fontsize=5.3, color="#b5483a", ha="center", va="top")
    fig.supxlabel("enrichment E = co-occurrence rate in fine-tuned output / rate in base-model output (log scale)",
                  fontsize=7)
    setting_legend(fig)
    save(fig, out, "enrichment")


# ---------------------------------------------------------------- largest tuple per profile
SIZE_COLOR = {"1": "#e8eef4", "2": "#9ebcda", "3": "#5a7fb8", "4": "#2b2f6b"}
SIZE_TEXT = {"1": INK, "2": INK, "3": "white", "4": "white"}


def largest_tuple(ls, out):
    rows = [(ds, s) for ds in spec.DATASETS for s in SETTINGS
            if not redundant_author(ds, 0, s) and f"{ds}|{s}" in ls]
    fig, ax = plt.subplots(figsize=(WIDTH, 2.4), layout="constrained")
    y, yt, yl, prev = 0, [], [], None
    for ds, s in rows:
        if ds != prev:       # dataset header row
            y += 0.35 if prev else 0
            yt.append(y)
            yl.append(DSNAME[ds])
            y += 0.85
        prev = ds
        m = ls[f"{ds}|{s}"]["substring"]["largest_group"]
        left = 0
        for g in "1234":
            v = m[g]["median"]
            ax.barh(y, v, left=left, height=0.72, color=SIZE_COLOR[g], edgecolor="white", lw=0.6)
            if v >= 45:
                ax.text(left + v / 2, y, f"{v:,}", ha="center", va="center", fontsize=6.3, color=SIZE_TEXT[g])
            left += v
        x = left + 18
        for g in "1234":     # segments too narrow for a label: coloured key and count after the bar
            v = m[g]["median"]
            if v < 45:
                ax.scatter([x], [y], marker="s", s=16, color=SIZE_COLOR[g], edgecolor="#777777", lw=0.4, zorder=3)
                ax.text(x + 14, y, f"{v:,}", ha="left", va="center", fontsize=6.0, color=INK)
                x += 70
        yt.append(y)
        yl.append(f"{STYLE[s]['label']} ({ls[f'{ds}|{s}']['substring']['profiles_leaked']['median']:,})")
        y += 1
    ax.set_yticks(yt, yl)
    for t in ax.get_yticklabels():
        if t.get_text() in DSNAME.values():
            t.set_fontweight("bold")
    ax.set_ylim(y - 0.4, -0.6)
    ax.tick_params(axis="y", length=0)
    ax.spines["left"].set_visible(False)
    ax.set_xlim(0, 1380)
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_xlabel("source profiles (notes) with at least one leaked value")
    ax.grid(axis="x", color=GRID, lw=0.5)
    ax.set_axisbelow(True)
    h = [Patch(alpha=0)] + [Patch(facecolor=SIZE_COLOR[g], edgecolor="#999999", lw=0.4) for g in "1234"]
    fig.legend(h, ["largest group in one document:", "1 value", "2 values", "3 values", "4 values"],
               loc="outside upper center", ncol=5, frameon=False, columnspacing=1.2, handlelength=1.6)
    save(fig, out, "largest_tuple")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO.parent / "paper" / "figures"))
    ap.add_argument("--tuples", nargs="+", default=["N,A,E"])
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    setup()
    cs = json.loads((REPO / "results" / "canary_summary.json").read_text())
    for tup in a.tuples:
        canary_exposure(cs, tup, out)
    lp = REPO / "results" / "leakage_runs.json"
    if lp.exists():
        leak = json.loads(lp.read_text())
        leakage_bars(leak, "singles_by_type", "single_top_leakage", 8, out, "unique leaked training values")
        leakage_bars(leak, "pairs_by_typepair", "combined_top_leakage", 8, out, "unique leaked type-distinct pairs")
    ls = json.loads((REPO / "results" / "leakage_summary.json").read_text())
    enrichment(ls, out)
    largest_tuple(ls, out)


if __name__ == "__main__":
    main()
