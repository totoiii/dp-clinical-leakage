#!/usr/bin/env python3
"""
Re-analysis for the BMC revision (Reviewer 2, R2.2 + R2.3).

Runs entirely on the already-generated corpora + human PII annotations.
No GPU, no retraining.

Outputs, per (dataset, epsilon) config:
  1. Comparable-units leakage: unique singles / unique type-distinct
     pairs / triples / quadruples  (reproduces Table 6, correctly described).
  2. Largest unique matched tuple per SOURCE profile (reviewer's suggested
     primary measure) + distribution over profiles -> avoids combinatorial
     double counting.
  3. Independence NULL MODEL: for every audited type-distinct value pair,
     observed doc-level co-occurrence in the synthetic corpus vs. the
     co-occurrence expected under marginal independence. Aggregated by
     PII type-pair as an enrichment ratio (observed / expected).
     Enrichment ~ 1  => chance co-occurrence (e.g. AGE,DATE).
     Enrichment >> 1  => memorized association (e.g. NAME,LOCATION).

Usage:
    python reanalysis.py                 # runs all configs, prints + writes JSON
"""
import os
import csv
import ast
import json
import itertools
from collections import defaultdict

csv.field_size_limit(10_000_000)

REPO = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ROOT = os.path.join(REPO, "results", "output")
DATA_ROOT = os.path.join(REPO, "data")

# Multi-entity tuples must have DISTINCT PII types; SEX is not an identifier.
EXCLUDED_TYPES_IN_MULTI = {"SEXO_SUJETO_ASISTENCIA"}

CONFIGS = {
    "i2b2": ["nodp", "8eps", "4eps"],
    "meddocan": ["nodp", "8eps", "4eps"],
}
ARITIES = ["single", "pairs", "triples", "quadruples"]
ARITY_N = {"single": 1, "pairs": 2, "triples": 3, "quadruples": 4}


def load_type_maps(dataset):
    """text(lower) -> type, and total unique PII count."""
    path = os.path.join(DATA_ROOT, dataset, "original_tags.csv")
    text_to_type = {}
    unique_per_type = defaultdict(set)
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)
        for row in r:
            if len(row) > 5 and row[5] and row[1]:
                t = row[1]
                txt = row[5].lower()
                text_to_type[txt] = t
                unique_per_type[t].add(txt)
    total_unique_pii = sum(len(v) for v in unique_per_type.values())
    return text_to_type, total_unique_pii


def type_of(text, text_to_type):
    return text_to_type.get(text.lower())


def valid_tuple(items, text_to_type):
    """Distinct values, distinct non-None types, no excluded type."""
    if len(items) != len(set(items)):
        return None
    types = [type_of(x, text_to_type) for x in items]
    if None in types:
        return None
    if len(types) != len(set(types)):
        return None
    if any(t in EXCLUDED_TYPES_IN_MULTI for t in types):
        return None
    return tuple(sorted(types))


def load_filtered_docs(config_dir):
    """List of sets: per generated doc, the training PII values it contains."""
    path = os.path.join(config_dir, "filtered_labels.csv")
    docs = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        for row in r:
            if len(row) >= 2:
                try:
                    labels = ast.literal_eval(row[1].strip())
                    docs.append(set(labels))
                except Exception:
                    pass
    return docs


def analyze_config(dataset, eps):
    config_dir = os.path.join(OUTPUT_ROOT, f"llama-1B-{dataset}-0can-common-{eps}")
    text_to_type, total_unique_pii = load_type_maps(dataset)
    with open(os.path.join(config_dir, "filtration_results.json")) as f:
        filt = json.load(f)

    # ---- (1) comparable-units unique counts + (2) largest tuple per profile ----
    unique_singles = set()
    unique_by_arity = {2: set(), 3: set(), 4: set()}
    per_profile_max = {}          # source file -> largest valid arity leaked
    # store the actual value-tuples for the null model (pairs only)
    audited_pairs = set()

    for fname, fdata in filt.items():
        if fname == "summary":
            continue
        max_here = 0
        # singles
        for item in fdata["texts"]["single"]:
            if item and type_of(item, text_to_type) is not None:
                unique_singles.add(item)
                max_here = max(max_here, 1)
        # multi
        for arity_name, n in (("pairs", 2), ("triples", 3), ("quadruples", 4)):
            for tup in fdata["texts"][arity_name]:
                vt = valid_tuple(tuple(tup), text_to_type)
                if vt is not None:
                    key = tuple(sorted(tup))
                    unique_by_arity[n].add(key)
                    max_here = max(max_here, n)
                    if n == 2:
                        audited_pairs.add(key)
        if max_here > 0:
            per_profile_max[fname] = max_here

    comparable = {
        "total_unique_pii": total_unique_pii,
        "unique_singles": len(unique_singles),
        "unique_singles_pct": round(100 * len(unique_singles) / total_unique_pii, 2),
        "unique_pairs": len(unique_by_arity[2]),
        "unique_triples": len(unique_by_arity[3]),
        "unique_quadruples": len(unique_by_arity[4]),
    }

    # distribution of largest matched tuple per profile
    dist = defaultdict(int)
    for m in per_profile_max.values():
        dist[m] += 1
    largest_tuple_dist = {
        "profiles_with_any_leak": len(per_profile_max),
        "largest_is_1": dist[1],
        "largest_is_2": dist[2],
        "largest_is_3": dist[3],
        "largest_is_4": dist[4],
    }

    # ---- (3) independence null model on pairs ----
    docs = load_filtered_docs(config_dir)
    n_docs = len(docs)
    # inverted index value -> set(doc ids)
    inv = defaultdict(set)
    for i, d in enumerate(docs):
        for v in d:
            inv[v].add(i)
    marg = {v: len(ids) / n_docs for v, ids in inv.items()}

    by_typepair_obs = defaultdict(float)
    by_typepair_exp = defaultdict(float)
    by_typepair_n = defaultdict(int)
    for (v1, v2) in audited_pairs:
        if v1 not in inv or v2 not in inv:
            continue
        observed = len(inv[v1] & inv[v2])           # docs with both
        expected = n_docs * marg[v1] * marg[v2]     # under independence
        tp = tuple(sorted([type_of(v1, text_to_type), type_of(v2, text_to_type)]))
        by_typepair_obs[tp] += observed
        by_typepair_exp[tp] += expected
        by_typepair_n[tp] += 1

    null_model = []
    for tp in sorted(by_typepair_obs, key=lambda k: -by_typepair_obs[k]):
        obs = by_typepair_obs[tp]
        exp = by_typepair_exp[tp]
        null_model.append({
            "type_pair": "+".join(tp),
            "n_unique_value_pairs": by_typepair_n[tp],
            "observed_cooccur_docs": round(obs, 1),
            "expected_cooccur_docs": round(exp, 2),
            "enrichment_obs_over_exp": round(obs / exp, 2) if exp > 0 else None,
        })

    return {
        "dataset": dataset,
        "epsilon": eps,
        "n_synthetic_docs": n_docs,
        "comparable_units": comparable,
        "largest_tuple_per_profile": largest_tuple_dist,
        "null_model_by_typepair": null_model,
    }


def main():
    all_results = {}
    for dataset, epsvals in CONFIGS.items():
        for eps in epsvals:
            key = f"{dataset}-{eps}"
            print(f"\n{'='*70}\n{key}\n{'='*70}")
            res = analyze_config(dataset, eps)
            all_results[key] = res
            c = res["comparable_units"]
            print(f"  Synthetic docs: {res['n_synthetic_docs']}")
            print(f"  [Comparable units] unique singles={c['unique_singles']} "
                  f"({c['unique_singles_pct']}%)  pairs={c['unique_pairs']}  "
                  f"triples={c['unique_triples']}  quads={c['unique_quadruples']}")
            d = res["largest_tuple_per_profile"]
            print(f"  [Largest tuple/profile] profiles_leaked={d['profiles_with_any_leak']}  "
                  f"max1={d['largest_is_1']} max2={d['largest_is_2']} "
                  f"max3={d['largest_is_3']} max4={d['largest_is_4']}")
            print(f"  [Null model] top type-pairs (observed vs expected co-occ, enrichment):")
            for row in res["null_model_by_typepair"][:8]:
                print(f"     {row['type_pair']:<28} obs={row['observed_cooccur_docs']:>8}  "
                      f"exp={row['expected_cooccur_docs']:>10}  "
                      f"enrich={row['enrichment_obs_over_exp']}")
    out = os.path.join(REPO, "reanalysis_results.json")
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
