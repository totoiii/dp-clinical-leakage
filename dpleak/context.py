"""
Clinical context of matched pairs (reviewer A.3.2), on whole-word matches.

    python -m dpleak.context --gens runs/i2b2_docs0_nodp_s42 runs/i2b2_docs0_eps8_record_s42 ... --dataset i2b2 --out results/context_i2b2.json [--sample-out runs/context_sample_i2b2.csv]

1. For every pair of type-distinct values from one source note that co-occur (as whole
   words) in one synthetic document, all training notes are ranked by TF-IDF cosine
   similarity to the witnessing document (annotated PII removed from both sides) and the
   rank of the source note is recorded (best witness when several; tied notes share the
   mean of their positions, so rank 1 means strictly most similar). Null: the same
   procedure with a uniformly drawn other note, 200 draws (mean and 95% interval).
2. Optionally, a stratified sample (25 pairs with a direct identifier, 25 with only
   quasi-identifiers; seed 42) is written for manual review. The sample file contains
   text windows from training notes and synthetic documents: it stays on the server.
"""
import argparse
import csv
import json
import random
import re
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from statistics import median

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from . import data
from .leakage import Annotations, read_generations

SEED, PER_STRATUM, WINDOW = 42, 25, 220
NULL_DRAWS = 200

# Direct identifiers: they name or contact the person.
DIRECT = {
    "i2b2": {"NAME", "ID", "CONTACT"},
    "meddocan": {"NOMBRE_SUJETO_ASISTENCIA", "NOMBRE_PERSONAL_SANITARIO", "ID_SUJETO_ASISTENCIA",
                 "ID_ASEGURAMIENTO", "ID_CONTACTO_ASISTENCIAL", "ID_TITULACION_PERSONAL_SANITARIO",
                 "CORREO_ELECTRONICO", "NUMERO_TELEFONO", "NUMERO_FAX", "CALLE"},
}


class _NG:
    """Adapter so the ported functions keep their original calls."""
    @staticmethod
    def valid_tuple(items, ann):
        return ann.valid(items)

    @staticmethod
    def type_of(v, ann):
        return ann.t(v)


NG = _NG()


def source_notes(dataset):
    tags = defaultdict(list)
    with open(data.DATA / dataset / "original_tags.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["Text"]:
                tags[r["Filename"]].append((int(r["Start"]), int(r["End"]), r["Text"], r["Tag Name"]))
    notes = {}
    for fname in sorted(tags):
        raw = (data.DATA / dataset / "original" / fname).read_text(encoding="utf-8", errors="ignore")
        mm = re.search(r"<TEXT><!\[CDATA\[(.*?)\]\]></TEXT>", raw, re.S)
        notes[fname] = mm.group(1) if mm else raw
    return notes, tags


def ww(value):
    return re.compile(r"(?<!\w)" + re.escape(value) + r"(?!\w)")


def strip_spans(text, spans):
    out, last = [], 0
    for s, e, *_ in sorted(spans):
        if s >= last:
            out.append(text[last:s]); last = e
    out.append(text[last:])
    return " ".join(out)


def strip_values(text, values):
    for v in sorted(values, key=len, reverse=True):
        text = ww(v).sub(" ", text)
    return text


def one_doc_pairs(dataset, docs, tags, text_to_type):
    """{(fuente, par): [ids de documentos donde ambos valores son palabra completa]}."""
    by_value = defaultdict(set)
    for fname, spans in tags.items():
        for *_, text, _t in spans:
            by_value[text].add(fname)
    hits = defaultdict(set)                       # fuente -> {(doc, valor)}
    for v, files in by_value.items():
        pat = ww(v)
        for i, d in enumerate(docs):
            if v in d and pat.search(d):
                for fname in files:
                    hits[fname].add((i, v))
    pairs = defaultdict(list)
    for fname, dv in hits.items():
        per_doc = defaultdict(set)
        for i, v in dv:
            per_doc[i].add(v)
        for i, vals in per_doc.items():
            for a, b in combinations(sorted(vals), 2):
                if NG.valid_tuple((a, b), text_to_type):
                    pairs[(fname, (a, b))].append(i)
    return pairs


def rank_of_source(notes, tags, pairs, docs):
    files = list(notes)
    idx = {f: k for k, f in enumerate(files)}
    clean_notes = [strip_spans(notes[f], tags[f]) for f in files]
    all_pii = {t for f in files for *_, t, _ in tags[f]}
    vec = TfidfVectorizer(lowercase=True, token_pattern=r"(?u)\b[^\W\d_]{3,}\b", sublinear_tf=True, min_df=2)
    N = vec.fit_transform(clean_notes)
    used = sorted({i for ids in pairs.values() for i in ids})
    D = vec.transform([strip_values(docs[i], [v for v in all_pii if v in docs[i]]) for i in used])
    sims = (D @ N.T).toarray()
    row = {i: k for k, i in enumerate(used)}
    rng = np.random.default_rng(SEED)

    def best_rank(col, ids):
        # Mid-rank for ties: a witness with no content term left (all similarities 0) puts
        # every note at the middle rank instead of tying them all at rank 1.
        def rank(i):
            s = sims[row[i]]
            return int((s > s[col]).sum()) + 1 + (int((s == s[col]).sum()) - 1) / 2
        return min(rank(i) for i in ids)

    # Orden fijo: el dict viene de sets de strings (orden depende de PYTHONHASHSEED),
    # y sin esto el RNG asigna notas distintas en cada corrida.
    keys = sorted(pairs)
    ranks = {k: best_rank(idx[k[0]], pairs[k]) for k in keys}
    # Nulo: misma métrica y mismos testigos, pero con una nota al azar distinta
    # de la fuente (corrige el sesgo de tomar el mejor testigo). Se repite
    # NULL_DRAWS veces; null[k] es la lista de rangos nulos del par k.
    null = {k: [] for k in keys}
    for _ in range(NULL_DRAWS):
        for k in keys:
            other = int(rng.integers(len(files) - 1))
            null[k].append(best_rank(other + (other >= idx[k[0]]), pairs[k]))
    return ranks, null, len(files)


def summarise(ranks, null, n_notes, direct, text_to_type):
    def is_direct(key):
        return any(NG.type_of(v, text_to_type) in direct for v in key[1])

    def block(keys):
        obs = [ranks[k] for k in keys]
        if not keys:
            return {"pairs": 0}
        draws = list(zip(*(null[k] for k in keys)))      # una tupla por sorteo
        r1 = [sum(r == 1 for r in d) for d in draws]
        t10 = [sum(r <= 10 for r in d) for d in draws]
        med = [median(d) for d in draws]
        q = lambda xs, p: float(np.percentile(xs, p))
        return {"pairs": len(keys), "null_draws": len(draws),
                "rank1": sum(r == 1 for r in obs),
                "rank1_null_mean": round(float(np.mean(r1)), 1), "rank1_null_95": [q(r1, 2.5), q(r1, 97.5)],
                "top10": sum(r <= 10 for r in obs),
                "top10_null_mean": round(float(np.mean(t10)), 1), "top10_null_95": [q(t10, 2.5), q(t10, 97.5)],
                "median_rank": median(obs),
                "median_rank_null_mean": round(float(np.mean(med)), 1), "median_rank_null_95": [q(med, 2.5), q(med, 97.5)]}
    keys = list(ranks)
    return {"all": block(keys), "with_direct_identifier": block([k for k in keys if is_direct(k)]),
            "n_notes": n_notes}


def window(text, value):
    m = ww(value).search(text)
    if not m:
        return ""
    return re.sub(r"\s+", " ", text[max(0, m.start() - WINDOW): m.end() + WINDOW])


def sample(dataset, pairs, ranks, docs, notes, text_to_type, rng):
    direct = DIRECT[dataset]
    strata = {"direct": [], "quasi": []}
    for key in sorted(pairs):
        types = {NG.type_of(v, text_to_type) for v in key[1]}
        strata["direct" if types & direct else "quasi"].append(key)
    rows = []
    for name, keys in strata.items():
        for fname, (a, b) in rng.sample(keys, min(PER_STRATUM, len(keys))):
            i = min(pairs[(fname, (a, b))])
            rows.append({
                "dataset": dataset, "stratum": name, "source_file": fname,
                "value_1": a, "type_1": NG.type_of(a, text_to_type),
                "value_2": b, "type_2": NG.type_of(b, text_to_type),
                "synthetic_doc_id": i, "source_rank": ranks[(fname, (a, b))],
                "synthetic_context_1": window(docs[i], a), "synthetic_context_2": window(docs[i], b),
                "source_context_1": window(notes[fname], a), "source_context_2": window(notes[fname], b),
                "same_clinical_context": "", "linkable_to_patient": "", "notes": "",
            })
    return rows, {k: len(v) for k, v in strata.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", nargs="+", required=True)
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sample-out")
    a = ap.parse_args()
    ds = a.dataset
    ann = Annotations(ds)
    notes, tags = source_notes(ds)
    summary = {}
    rng = random.Random(SEED)
    for g in a.gens:
        g = Path(g)
        docs = read_generations(g / "generations.csv")
        pairs = one_doc_pairs(ds, docs, tags, ann)
        ranks, null, n_notes = rank_of_source(notes, tags, pairs, docs)
        summary[g.name] = summarise(ranks, null, n_notes, DIRECT[ds], ann)
        print(g.name, json.dumps(summary[g.name]["all"]), flush=True)
        if a.sample_out and g == Path(a.gens[0]):
            rows, sizes = sample(ds, pairs, ranks, docs, notes, ann, rng)
            summary[g.name]["strata_population"] = sizes
            with open(a.sample_out, "w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0]))
                w.writeheader()
                w.writerows(rows)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
