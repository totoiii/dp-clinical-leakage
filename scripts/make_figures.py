#!/usr/bin/env python3
"""
Figures of the manuscript from results/canary_summary.json.

    python scripts/make_figures.py --out ../paper/figures

canary_exposure.pdf: rank of the inserted profile against exposure (0 = no-canary model),
one panel per dataset x tagset, one line per privacy setting, for the tuples given by
--tuples (median over training seeds, bars = min-max). Log scale, rank 1 at the top,
dotted line = chance (5,000).
single_top_leakage.pdf / combined_top_leakage.pdf: unique leaked training values per PII
type, and leaked type-distinct pairs per type pair, in the 1,000 documents of each model
(substring matching, median over training seeds), from results/leakage_runs.json.
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from dpleak import spec  # noqa: E402

STYLE = {  # colour-blind-safe (Okabe-Ito); record = solid, author = dashed
    "nodp": dict(color="#000000", ls="-", marker="o", label="Non-DP"),
    "eps8_record": dict(color="#0072B2", ls="-", marker="s", label="ε=8, record"),
    "eps4_record": dict(color="#56B4E9", ls="-", marker="^", label="ε=4, record"),
    "eps8_author": dict(color="#D55E00", ls="--", marker="s", label="ε=8, author"),
    "eps4_author": dict(color="#E69F00", ls="--", marker="^", label="ε=4, author"),
}
DSNAME = {"i2b2": "i2b2 2014", "meddocan": "MEDDOCAN"}
EXPOSURES = (0, 1, 10, 100)


def series(cs, ds, tag, setting, tup):
    xs, med, lo, hi = [], [], [], []
    for i, k in enumerate(EXPOSURES):
        role = "no_canary_model" if k == 0 else "inserted"
        e = cs.get(f"{ds}|docs{k}|{tag}|{setting}|{role}", {}).get(tup, {}).get("rank")
        if e:
            xs.append(i)
            med.append(e["median"])
            lo.append(e["median"] - e["min"])
            hi.append(e["max"] - e["median"])
    return xs, med, lo, hi


TYPE_EN = {"EDAD_SUJETO_ASISTENCIA": "AGE", "FECHAS": "DATE", "TERRITORIO": "TERRITORY", "PAIS": "COUNTRY",
           "NOMBRE_SUJETO_ASISTENCIA": "NAME", "NOMBRE_PERSONAL_SANITARIO": "CLINICIAN NAME", "CALLE": "STREET",
           "HOSPITAL": "HOSPITAL", "INSTITUCION": "INSTITUTION", "ID_SUJETO_ASISTENCIA": "PATIENT ID",
           "ID_TITULACION_PERSONAL_SANITARIO": "LICENCE NO.", "ID_CONTACTO_ASISTENCIAL": "CONTACT ID",
           "PROFESION": "PROFESSION", "FAMILIARES_SUJETO_ASISTENCIA": "RELATIVES", "OTROS_SUJETO_ASISTENCIA": "OTHER",
           "SEXO_SUJETO_ASISTENCIA": "SEX", "CORREO_ELECTRONICO": "EMAIL", "NUMERO_TELEFONO": "PHONE",
           "NUMERO_FAX": "FAX", "ID_ASEGURAMIENTO": "INSURANCE ID", "ID_EMPLEO_PERSONAL_SANITARIO": "EMPLOYEE ID",
           "CENTRO_SALUD": "HEALTH CENTRE", "URL_WEB": "URL", "IDENTIF_DISPOSITIVOS_NRSERIE": "DEVICE ID",
           "OTRO_NUMERO_IDENTIF": "OTHER ID", "IDENTIF_VEHICULOS_NRSERIE_PLACAS": "VEHICLE ID",
           "DIREC_PROT_INTERNET": "IP", "IDENTIF_BIOMETRICOS": "BIOMETRIC", "NUMERO_BENEF_PLAN_SALUD": "PLAN NO.",
           "ID_TITULACION": "LICENCE NO."}
LEAK_SETTINGS = ["nodp", "eps8_record", "eps4_record", "eps8_author", "eps4_author"]


def leak_counts(leak, ds, field, mode="substring"):
    """{setting: {label: median count over training seeds}} for field singles_by_type or pairs_by_typepair."""
    import statistics as st
    from collections import defaultdict
    out = {}
    for s in LEAK_SETTINGS:
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
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.0))
    for ax, ds in zip(axes, spec.DATASETS):
        c = leak_counts(leak, ds, field)
        labels = sorted(c["nodp"], key=lambda t: -c["nodp"][t])[:top][::-1]
        sets = [s for s in LEAK_SETTINGS if s in c]
        h = 0.8 / len(sets)
        for i, s in enumerate(sets):
            ys = [j + (i - (len(sets) - 1) / 2) * h for j in range(len(labels))]
            ax.barh(ys, [c[s].get(t, 0) for t in labels], height=h, color=STYLE[s]["color"],
                    hatch="//" if s.endswith("author") else None, edgecolor="white", lw=0.3, label=STYLE[s]["label"])
        ax.set_yticks(range(len(labels)), labels, fontsize=6.5)
        ax.set_title(DSNAME[ds])
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", lw=0.3, alpha=0.5)
    handles, labs = axes[0].get_legend_handles_labels()
    fig.legend(handles, labs, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(out / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("wrote", out / f"{name}.pdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO.parent / "paper" / "figures"))
    ap.add_argument("--tuples", nargs="+", default=["N,A,E", "A"])
    a = ap.parse_args()
    cs = json.loads((REPO / "results" / "canary_summary.json").read_text())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "legend.fontsize": 7})
    for tup in a.tuples:
        fig, axes = plt.subplots(1, 4, figsize=(7.2, 2.3), sharey=True)
        for ax, (ds, tag) in zip(axes, [(d, t) for d in spec.DATASETS for t in spec.TAGSETS]):
            for s, sty in STYLE.items():
                xs, med, lo, hi = series(cs, ds, tag, s, tup)
                if xs:
                    off = (list(STYLE).index(s) - 2) * 0.06
                    ax.errorbar([x + off for x in xs], med, yerr=[lo, hi], color=sty["color"], ls=sty["ls"],
                                marker=sty["marker"], ms=3.5, lw=1.1, capsize=1.5, label=sty["label"])
            ax.axhline(5000, color="grey", lw=0.6, ls=":")
            ax.set_yscale("log")
            ax.set_ylim(15000, 0.7)
            ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
            ax.set_xticks(range(len(EXPOSURES)), [str(k) for k in EXPOSURES])
            ax.set_xlabel("canary documents")
            ax.set_title(f"{DSNAME[ds]}, Tagset {tag}")
            ax.grid(axis="y", lw=0.3, alpha=0.5)
        axes[0].set_ylabel(f"rank of ({tup.replace(',', ', ')})")
        h, l = axes[0].get_legend_handles_labels()
        fig.legend(h, l, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.04))
        fig.tight_layout(rect=(0, 0.1, 1, 1))
        name = "canary_exposure_" + tup.replace(",", "")
        fig.savefig(out / f"{name}.pdf", bbox_inches="tight")
        fig.savefig(out / f"{name}.png", dpi=200, bbox_inches="tight")
        plt.close(fig)
        print("wrote", out / f"{name}.pdf")
    lp = REPO / "results" / "leakage_runs.json"
    if lp.exists():
        leak = json.loads(lp.read_text())
        leakage_bars(leak, "singles_by_type", "single_top_leakage", 8, out, "unique leaked values")
        leakage_bars(leak, "pairs_by_typepair", "combined_top_leakage", 8, out, "unique leaked pairs")


if __name__ == "__main__":
    main()
