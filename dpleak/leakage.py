"""
Multi-entity (tuple) leakage audit of a synthetic corpus against the training PII.

    python -m dpleak.leakage --gen runs/i2b2_docs0_nodp_s42 --dataset i2b2
    python -m dpleak.leakage --all            # every generated corpus under runs/

Definitions (as in the manuscript):
  * a training PII value "appears" in a generated document if it occurs as a substring
    (legacy matching) or as a whole word (delimited by non-word characters);
  * single leakage: distinct training values that appear in some document
    (share of all distinct annotated values, case-insensitive per type);
  * n-tuple leakage (n=2..4): distinct sets of n values with pairwise-distinct types
    (sex excluded), all taken from ONE source note, that co-occur in ONE generated
    document (different tuples of a note may be witnessed by different documents);
  * largest matched tuple per profile: for every source note, the largest such tuple
    contained in a single generated document; pairs_one_doc = sum_k C(k,2) n_k;
  * type-pair co-occurrence rate (for the generative-null enrichment): number of
    (document, value pair) co-occurrences per document for each PII type pair,
    (a) over any two typed training values (legacy definition), and
    (b) restricted to pairs from one source note.
Writes leakage.json next to generations.csv (aggregate counts only, no text).
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from math import comb
from pathlib import Path

from . import data, spec

csv.field_size_limit(10**9)
EXCLUDED_IN_TUPLES = {"SEXO_SUJETO_ASISTENCIA"}
REPO = Path(__file__).resolve().parent.parent


class Annotations:
    def __init__(self, dataset):
        d = data.DATA / dataset
        with open(d / "all_labels.csv", newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            next(r)
            self.values = sorted({row[0] for row in r if row and row[0]})
        self.type_of = {}
        per_type = defaultdict(set)
        self.by_file = defaultdict(list)
        with open(d / "original_tags.csv", newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                if len(row) > 5 and row[5] and row[1]:
                    self.type_of[row[5].lower()] = row[1]
                    per_type[row[1]].add(row[5].lower())
                if len(row) > 5 and row[5]:
                    self.by_file[row[0]].append(row[5])
        self.total_unique = sum(len(v) for v in per_type.values())
        self.unique_per_type = {k: len(v) for k, v in per_type.items()}

    def t(self, v):
        return self.type_of.get(v.lower())

    def valid(self, items):
        if len(items) != len(set(items)):
            return None
        ts = [self.t(x) for x in items]
        if None in ts or len(ts) != len(set(ts)) or any(x in EXCLUDED_IN_TUPLES for x in ts):
            return None
        return tuple(sorted(ts))


def read_generations(path):
    with open(path, newline="", encoding="utf-8") as f:
        return [r["sequence"] for r in csv.DictReader(f) if r.get("sequence")]


def match(docs, values, whole_word=False):
    """Per document, the set of training values it contains."""
    out = []
    pats = {}
    for d in docs:
        hits = {v for v in values if v in d}
        if whole_word:
            keep = set()
            for v in hits:
                p = pats.get(v)
                if p is None:
                    p = pats[v] = re.compile(r"(?<!\w)" + re.escape(v) + r"(?!\w)")
                if p.search(d):
                    keep.add(v)
            hits = keep
        out.append(hits)
    return out


def audit(ann: Annotations, doc_sets):
    inv = defaultdict(set)
    for i, s in enumerate(doc_sets):
        for v in s:
            inv[v].add(i)
    singles = set()
    tuples = {2: set(), 3: set(), 4: set()}
    largest = Counter()
    singles_by_type = Counter()
    pairs_by_typepair = Counter()
    for fname, texts in ann.by_file.items():
        present = sorted({t for t in texts if t in inv})
        big = 0
        for v in present:
            if ann.t(v):
                singles.add(v)
                big = 1
        for n in (2, 3, 4):
            for c in combinations(present, n):
                vt = ann.valid(c)
                if vt is None:
                    continue
                if set.intersection(*(inv[x] for x in c)):
                    key = tuple(sorted(c))
                    if n == 2 and key not in tuples[2]:
                        pairs_by_typepair["+".join(vt)] += 1
                    tuples[n].add(key)
                    big = max(big, n)
        if big:
            largest[big] += 1
    for v in singles:
        singles_by_type[ann.t(v)] += 1
    return dict(
        n_docs=len(doc_sets), total_unique_pii=ann.total_unique,
        singles=len(singles), singles_pct=round(100 * len(singles) / ann.total_unique, 2),
        pairs=len(tuples[2]), triples=len(tuples[3]), quadruples=len(tuples[4]),
        profiles_leaked=sum(largest.values()),
        largest_group={str(k): largest[k] for k in (1, 2, 3, 4)},
        pairs_one_doc=sum(comb(k, 2) * largest[k] for k in (2, 3, 4)),
        singles_by_type=dict(singles_by_type.most_common()),
        pairs_by_typepair=dict(pairs_by_typepair.most_common()),
    )


def typepair_rates(ann: Annotations, doc_sets):
    """(a) any-value and (b) same-source co-occurrences per document, by type pair."""
    n = len(doc_sets)
    any_obs = Counter()
    for s in doc_sets:
        typed = sorted(v for v in s if ann.t(v))
        for v1, v2 in combinations(typed, 2):
            vt = ann.valid((v1, v2))
            if vt:
                any_obs["+".join(vt)] += 1
    # same-source: value pairs that belong to one source note
    same_pairs = defaultdict(set)
    for texts in ann.by_file.values():
        u = sorted(set(texts))
        for c in combinations(u, 2):
            vt = ann.valid(c)
            if vt:
                same_pairs[c].add("+".join(vt))
    inv = defaultdict(set)
    for i, s in enumerate(doc_sets):
        for v in s:
            inv[v].add(i)
    same_obs = Counter()
    for (v1, v2), tps in same_pairs.items():
        if v1 in inv and v2 in inv:
            co = len(inv[v1] & inv[v2])
            if co:
                for tp in tps:
                    same_obs[tp] += co
    return dict(n_docs=n,
                any_per_doc={k: v / n for k, v in any_obs.most_common()},
                same_source_per_doc={k: v / n for k, v in same_obs.most_common()})


def analyze(gen_dir: Path, dataset: str):
    ann = Annotations(dataset)
    docs = read_generations(gen_dir / "generations.csv")
    res = dict(dataset=dataset, n_docs=len(docs))
    for mode, ww in (("substring", False), ("whole_word", True)):
        sets = match(docs, ann.values, ww)
        res[mode] = audit(ann, sets)
        res[mode]["typepair_rates"] = typepair_rates(ann, sets)
    (gen_dir / "leakage.json").write_text(json.dumps(res, indent=1))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen")
    ap.add_argument("--dataset")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--runs-dir", default=str(REPO / "runs"))
    a = ap.parse_args()
    if a.all:
        rd = Path(a.runs_dir)
        for g in sorted(rd.glob("*/generation.json")) + sorted(rd.glob("base/*/generation.json")):
            d = g.parent
            if (d / "leakage.json").exists() and (d / "leakage.json").stat().st_mtime > g.stat().st_mtime:
                continue
            ds = json.loads(g.read_text())["dataset"]
            r = analyze(d, ds)
            s = r["whole_word"]
            print(f"{d.name}: singles={s['singles']} pairs={s['pairs']} one-doc={s['pairs_one_doc']} "
                  f"triples={s['triples']} quads={s['quadruples']}", flush=True)
    else:
        analyze(Path(a.gen), a.dataset)


if __name__ == "__main__":
    main()
