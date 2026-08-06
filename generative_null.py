#!/usr/bin/env python3
"""
GENERATIVE-NULL comparison (rigorous, apples-to-apples).

Applies the SAME co-occurrence function to base-model vs fine-tuned
filtered_labels.csv, per-document normalized, for both datasets and all
privacy budgets. Enrichment = (fine-tuned per-doc rate) / (base per-doc rate).

  enrichment ~ 1  -> co-occurrence no greater than an untrained model => chance
  enrichment >> 1 -> fine-tuning induced the association => memorization
  enrichment = inf -> base model never produces it (pure memorization)

Base rate = the generative null the reviewer requested (Llama-3.2-1B, no FT,
same prompt/sampling/#docs, same substring matching).
"""
import os, csv, ast, json, itertools
from collections import defaultdict
csv.field_size_limit(10**7)
REPO = os.path.dirname(os.path.abspath(__file__))
EXCL = {"SEXO_SUJETO_ASISTENCIA"}
DATASETS = ["i2b2", "meddocan"]
EPS = ["nodp", "8eps", "4eps"]


def type_maps(ds):
    m = {}
    with open(f"{REPO}/data/{ds}/original_tags.csv", encoding="utf-8") as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) > 5 and row[5] and row[1]:
                m[row[5].lower()] = row[1]
    return m


def tof(t, m): return m.get(t.lower())


def vtup(items, m):
    if len(items) != len(set(items)): return None
    ts = [tof(x, m) for x in items]
    if None in ts or len(ts) != len(set(ts)): return None
    if any(t in EXCL for t in ts): return None
    return tuple(sorted(ts))


def load(fp):
    docs = []
    with open(fp, encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                try: docs.append(set(ast.literal_eval(row[1].strip())))
                except Exception: pass
    return docs


def rates(docs, m):
    n = len(docs); inv = defaultdict(set)
    for i, d in enumerate(docs):
        for v in d: inv[v].add(i)
    typed = [v for v in inv if tof(v, m)]
    obs = defaultdict(float)
    for v1, v2 in itertools.combinations(typed, 2):
        vt = vtup((v1, v2), m)
        if vt is None: continue
        co = len(inv[v1] & inv[v2])
        if co > 0: obs["+".join(vt)] += co
    return n, obs, len(typed)


def main():
    out = {}
    for ds in DATASETS:
        base_fp = f"{REPO}/null_base/{ds}/filtered_labels.csv"
        if not os.path.isfile(base_fp):
            print(f"[skip] {ds}: base generations not ready yet")
            continue
        m = type_maps(ds)
        base_n, base_obs, base_vals = rates(load(base_fp), m)
        out[ds] = {"base_docs": base_n, "base_distinct_values": base_vals, "by_eps": {}}
        print(f"\n{'='*66}\n{ds}: base={base_n} docs ({base_vals} distinct PII values matched)\n{'='*66}")
        for eps in EPS:
            ft_fp = f"{REPO}/results/output/llama-1B-{ds}-0can-common-{eps}/filtered_labels.csv"
            if not os.path.isfile(ft_fp):
                continue
            ft_n, ft_obs, ft_vals = rates(load(ft_fp), m)
            rows = {}
            for k in set(base_obs) | set(ft_obs):
                br = base_obs.get(k, 0) / base_n
                fr = ft_obs.get(k, 0) / ft_n
                rows[k] = {"base_per_doc": round(br, 4),
                           "ft_per_doc": round(fr, 4),
                           "enrichment_ft_over_base": (round(fr / br, 2) if br > 0 else None)}
            out[ds]["by_eps"][eps] = {"ft_docs": ft_n, "ft_distinct_values": ft_vals, "pairs": rows}
            print(f"\n-- {eps} (ft={ft_n} docs) --")
            print(f"{'type-pair':<24}{'base/doc':>9}{'ft/doc':>10}{'ft/base':>9}")
            for k in sorted(rows, key=lambda x: -(rows[x]['ft_per_doc']))[:10]:
                r = rows[k]
                e = r['enrichment_ft_over_base']
                print(f"{k:<24}{r['base_per_doc']:>9}{r['ft_per_doc']:>10}"
                      f"{(str(e)+'x') if e else 'inf':>9}")
    with open(f"{REPO}/generative_null_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nWrote {REPO}/generative_null_results.json")


if __name__ == "__main__":
    main()
