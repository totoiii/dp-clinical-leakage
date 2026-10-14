#!/usr/bin/env python3
"""
Collect every per-run output under runs/ into the aggregate result files that the
paper tables are built from (results/*.json; no text, no PII values of real patients).

    python scripts/aggregate.py            # after the queue and `python -m dpleak.leakage --all`

results/runs_index.json        one row per finished training run: privacy accounting, utility
results/canary_ranks.json      ranks per run, inserted and non-inserted profile
results/canary_summary.json    per condition x tuple: median and range over training seeds
results/leakage_runs.json      leakage metrics per generated corpus (fine-tuned and base)
results/leakage_summary.json   per dataset x setting: median and range over training seeds,
                               and enrichment against the base model (paired by seed index)
results/legacy_rescore.json    the published adapters re-scored with the pinned canary values
"""
import json
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from dpleak import spec  # noqa: E402

RUNS = REPO / "runs"
RES = REPO / "results"


def setting(r):
    """Column label of a run: nodp | eps8_record | eps8_author | ..."""
    return "nodp" if r.budget == "nodp" else f"{r.budget}_{r.unit}"


def cond_key(r):
    return f"{r.dataset}|{r.canary}{r.exposure}|{r.tagset or '-'}|{setting(r)}"


def summ(xs):
    xs = [x for x in xs if x is not None]
    if not xs:
        return None
    return dict(median=st.median(xs), min=min(xs), max=max(xs), n=len(xs), values=xs)


def rank_value(entry):
    """Rank of one tuple: the candidate-seed-0 draw (singles have one deterministic set);
    also the median over the three candidate draws for multi-entity tuples."""
    seeds = sorted(entry)
    return entry["0"]["rank"], st.median(entry[s]["rank"] for s in seeds)


def main():
    RES.mkdir(exist_ok=True)
    index, ranks = {}, {}
    for d in sorted(RUNS.iterdir()):
        if not (d / "run.json").exists():
            continue
        r = spec.parse_run_id(d.name)
        meta = json.loads((d / "run.json").read_text())
        index[r.id] = dict(
            condition=cond_key(r), seed=r.seed, steps=meta["steps"], privacy=meta["privacy"],
            utility_ppl_train200=meta["utility_ppl_train200"], nll_heldout=meta["nll_heldout"],
            final_train_loss=meta["final_train_loss_last50"], wall_s=meta["wall_s"], gpu=meta["gpu"],
            n_train_records=meta["n_train_records"], canary_records_in_train=meta["canary_records_in_train"],
            git=meta.get("git"))
        if (d / "ranks.json").exists():
            ranks[r.id] = json.loads((d / "ranks.json").read_text())
    (RES / "runs_index.json").write_text(json.dumps(index, indent=1))
    (RES / "canary_ranks.json").write_text(json.dumps(ranks, indent=1))

    # canary summary: inserted profile, and the non-inserted profile of the same model
    groups = defaultdict(lambda: defaultdict(list))
    for rid, rr in ranks.items():
        r = spec.parse_run_id(rid)
        for tagset, tuples in rr["ranks"].items():
            role = ("inserted" if r.exposure and tagset == r.tagset else
                    "no_canary_model" if r.exposure == 0 else "other_profile")
            key = f"{r.dataset}|{r.canary}{r.exposure}|{tagset}|{setting(r)}|{role}"
            for tup, entry in tuples.items():
                r0, rmed = rank_value(entry)
                groups[key][tup].append((r.seed, r0, rmed, entry["0"]["ppl_true"]))
    summary = {}
    for key, tuples in sorted(groups.items()):
        summary[key] = {}
        for tup, vals in tuples.items():
            vals.sort()
            summary[key][tup] = dict(
                seeds=[v[0] for v in vals],
                rank=summ([v[1] for v in vals]),
                rank_median_over_candidate_draws=summ([v[2] for v in vals]),
                ppl_true=summ([v[3] for v in vals]))
    (RES / "canary_summary.json").write_text(json.dumps(summary, indent=1))

    # leakage
    leak = {}
    for f in sorted(RUNS.glob("*/leakage.json")) + sorted(RUNS.glob("base/*/leakage.json")):
        leak[f.parent.name] = json.loads(f.read_text())
    (RES / "leakage_runs.json").write_text(json.dumps(leak, indent=1))
    lsum = {}
    metrics = ("singles", "singles_pct", "pairs", "pairs_one_doc", "triples", "quadruples", "profiles_leaked")
    for ds in spec.DATASETS:
        base = {int(k.split("_g")[1]): v for k, v in leak.items() if k.startswith(f"{ds}_g")}
        sets = defaultdict(dict)
        for k, v in leak.items():
            if k.startswith(f"{ds}_docs0_"):
                r = spec.parse_run_id(k)
                sets[setting(r)][r.seed] = v
        if base:
            sets["base"] = base
        for st_name, by_seed in sets.items():
            out = {"seeds": sorted(by_seed)}
            for mode in ("substring", "whole_word"):
                out[mode] = {m: summ([by_seed[s][mode][m] for s in sorted(by_seed)]) for m in metrics}
                out[mode]["largest_group"] = {
                    g: summ([by_seed[s][mode]["largest_group"][g] for s in sorted(by_seed)]) for g in "1234"}
                if st_name != "base" and base:
                    # pair the i-th training seed with the i-th base corpus
                    enr = defaultdict(lambda: defaultdict(list))
                    for i, s in enumerate(sorted(by_seed)):
                        b = base[sorted(base)[i % len(base)]][mode]["typepair_rates"]
                        f_ = by_seed[s][mode]["typepair_rates"]
                        for kind in ("any_per_doc", "same_source_per_doc"):
                            for tp, rate in f_[kind].items():
                                br = b[kind].get(tp, 0.0)
                                enr[kind][tp].append(rate / br if br > 0 else float("inf"))
                    out[mode]["enrichment"] = {
                        kind: {tp: summ(v) for tp, v in d.items()} for kind, d in enr.items()}
            lsum[f"{ds}|{st_name}"] = out
    (RES / "leakage_summary.json").write_text(json.dumps(lsum, indent=1, default=str))

    # legacy re-score
    leg = {}
    for f in sorted((RES / "legacy_rescore").glob("*.json")):
        leg[f.stem] = json.loads(f.read_text())["ranks"]
    if leg:
        (RES / "legacy_rescore.json").write_text(json.dumps(leg, indent=1))
    print(f"runs={len(index)} scored={len(ranks)} corpora={len(leak)} legacy={len(leg)}")


if __name__ == "__main__":
    main()
