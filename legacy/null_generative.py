#!/usr/bin/env python3
"""
GENERATIVE NULL MODEL for the BMC revision (Reviewer 2, R2.3).

Replicates the paper's generation + leakage-matching pipeline EXACTLY, but with
the NON-fine-tuned base model (meta-llama/Llama-3.2-1B). This gives the baseline
the reviewer asked for: how often do training-set PII values / tuples co-occur in
text from a model that never saw the clinical corpus? Co-occurrence in the
fine-tuned model ABOVE this base rate is memorization, not chance.

Faithful to the paper:
  * same base model:        meta-llama/Llama-3.2-1B  (no LoRA adapters)
  * same prompt:            en/es clinical prompt (utils.create_prompt_completion)
  * same sampling:          length=512, temperature=1.0, top_k=50, top_p=0.95,
                            repetition_penalty=1.0, do_sample=True
  * same #docs:             1000 per dataset (default)
  * same matching:          substring match vs all_labels.csv (evaluation.py:217)
  * same tuple counting:    analyze_filtered_texts (inlined verbatim from utils.py)

Only difference vs paper = the model is not fine-tuned. Everything else identical.

Usage:
  python null_generative.py --stage generate --dataset i2b2     --num 1000
  python null_generative.py --stage generate --dataset meddocan --num 1000
  python null_generative.py --stage analyze  --dataset i2b2
  python null_generative.py --stage analyze  --dataset meddocan
  python null_generative.py --stage all      --dataset i2b2     --num 1000
"""
import os
import csv
import ast
import json
import argparse
import itertools
from collections import defaultdict

csv.field_size_limit(10_000_000)

REPO = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.path.join(REPO, "data")
NULL_ROOT = os.path.join(REPO, "null_base")
BASE_MODEL = os.environ.get("BASE_MODEL", "meta-llama/Llama-3.2-1B")  # HF id or local path (no LoRA)

# ---- EXACT prompts (verbatim from src/utils.py create_prompt_completion) ----
EN_PROMPT = (""" Generate a hospital admission clinical report from scratch, ensuring medical accuracy, logical coherence, and consistency across all sections.
                                                You must invent all the medical and patient information, but make sure it is coherent and realistic.
                                                Medical report:
                                                """)
ES_PROMPT = (""" Genera un reporte clinico desde cero de un ingreso hospitalario, asegurando precisión médica, coherencia logica y consistencia en todas las secciones.
                        Debes inventar toda la información médica y del paciente, pero asegurate de que sea coherente y realista.
                                                Reporte clinico:
                                                """)
LANG = {"i2b2": ("en", EN_PROMPT), "meddocan": ("es", ES_PROMPT)}

# Multi-entity tuples must have DISTINCT PII types; SEX is not an identifier.
EXCLUDED_TYPES_IN_MULTI = {"SEXO_SUJETO_ASISTENCIA"}


# ============================ GENERATION STAGE ============================
def stage_generate(dataset, num, batch):
    import torch
    import transformers

    lang, prompt_text = LANG[dataset]
    out_dir = os.path.join(NULL_ROOT, dataset)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "generations.csv")

    device = "mps" if torch.backends.mps.is_available() else (
        "cuda" if torch.cuda.is_available() else "cpu")
    print(f"[generate] dataset={dataset} lang={lang} device={device} "
          f"target={num} docs batch={batch}")

    tok = transformers.AutoTokenizer.from_pretrained(BASE_MODEL)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token          # base model has no pad token
    model = transformers.AutoModelForCausalLM.from_pretrained(
        BASE_MODEL, torch_dtype=torch.float16)
    model.to(device)
    model.eval()

    prompt_ids = tok(prompt_text)["input_ids"]
    prompt_len = len(prompt_text)              # char strip, as in generate_text.py

    with open(out_path, "w", newline="", encoding="utf-8") as wf:
        csv.writer(wf).writerow(["sequence", "ppl"])

    made = 0
    import time
    t0 = time.time()
    while made < num:
        b = min(batch, num - made)
        input_ids = torch.tensor(prompt_ids, device=device).repeat(b, 1)
        attention_mask = (input_ids != tok.pad_token_id).long()
        with torch.no_grad():
            output = model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_length=512,
                temperature=1.0,
                top_k=50,
                top_p=0.95,
                early_stopping=True,
                repetition_penalty=1.0,
                do_sample=True,
                num_return_sequences=1,
            )
        seqs = tok.batch_decode(output, skip_special_tokens=True,
                                clean_up_tokenization_spaces=True)
        with open(out_path, "a", newline="", encoding="utf-8") as wf:
            w = csv.writer(wf)
            for s in seqs:
                text = s[prompt_len:].strip()
                if text:
                    w.writerow([text, ""])
        made += b
        print(f"  {made}/{num}  ({time.time()-t0:.0f}s)")
    print(f"[generate] wrote {out_path}")


# ==================== MATCHING (verbatim evaluation.py:217) ====================
def build_filtered_labels(dataset):
    out_dir = os.path.join(NULL_ROOT, dataset)
    gen_path = os.path.join(out_dir, "generations.csv")
    labels_path = os.path.join(DATA_ROOT, dataset, "all_labels.csv")

    original_pii_labels = []
    with open(labels_path, newline="", encoding="utf-8") as rf:
        r = csv.reader(rf); next(r)
        for row in r:
            if row and row[0]:
                original_pii_labels.append(row[0])

    generated_seqs = []
    with open(gen_path, newline="", encoding="utf-8") as rf:
        r = csv.reader(rf); next(r)
        for row in r:
            if row:
                generated_seqs.append(row[0])

    fpath = os.path.join(out_dir, "filtered_labels.csv")
    with open(fpath, "w", newline="", encoding="utf-8") as wf:
        w = csv.writer(wf)
        for seq in generated_seqs:
            filtered = [lab for lab in original_pii_labels if lab in seq]  # substring
            w.writerow([seq, filtered])
    print(f"[match] {len(generated_seqs)} base docs -> {fpath}")
    return fpath, len(generated_seqs)


# ============ TUPLE COUNTING (inlined verbatim from utils.py) ============
def analyze_filtered_texts(all_labels, filtered_labels_path):
    filtered_labels_lists = []
    with open(filtered_labels_path, "r") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                try:
                    filtered_labels_lists.append(ast.literal_eval(row[1].strip()))
                except Exception:
                    pass
    all_filtered_texts = set()
    for labels in filtered_labels_lists:
        all_filtered_texts.update(labels)
    filename_to_texts = defaultdict(list)
    for label in all_labels:
        if label[5]:
            filename_to_texts[label[0]].append(label[5])

    results = {}
    for filename, texts in filename_to_texts.items():
        results[filename] = {"count": {k: 0 for k in
                             ("single", "pairs", "triples", "quadruples")},
                             "texts": {k: [] for k in
                             ("single", "pairs", "triples", "quadruples")}}
        valid = [t for t in texts if t in all_filtered_texts]
        if valid:
            for text in valid:
                for fl in filtered_labels_lists:
                    if text in fl:
                        results[filename]["count"]["single"] += 1
                        results[filename]["texts"]["single"].append(text); break
        for n, name in ((2, "pairs"), (3, "triples"), (4, "quadruples")):
            if len(valid) >= n:
                for combo in itertools.combinations(valid, n):
                    for fl in filtered_labels_lists:
                        if all(t in fl for t in combo):
                            results[filename]["count"][name] += 1
                            results[filename]["texts"][name].append(combo); break
    return results


# ============================ ANALYSIS STAGE ============================
def load_type_maps(dataset):
    path = os.path.join(DATA_ROOT, dataset, "original_tags.csv")
    text_to_type, unique_per_type = {}, defaultdict(set)
    all_tags = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f); next(r)
        for row in r:
            all_tags.append(row)
            if len(row) > 5 and row[5] and row[1]:
                text_to_type[row[5].lower()] = row[1]
                unique_per_type[row[1]].add(row[5].lower())
    return text_to_type, all_tags, sum(len(v) for v in unique_per_type.values())


def type_of(t, m): return m.get(t.lower())


def valid_tuple(items, m):
    if len(items) != len(set(items)): return None
    types = [type_of(x, m) for x in items]
    if None in types or len(types) != len(set(types)): return None
    if any(t in EXCLUDED_TYPES_IN_MULTI for t in types): return None
    return tuple(sorted(types))


def load_docs(filtered_path):
    docs = []
    with open(filtered_path, newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row) >= 2:
                try:
                    docs.append(set(ast.literal_eval(row[1].strip())))
                except Exception:
                    pass
    return docs


def cooccur_by_typepair(docs, text_to_type):
    """Doc-level co-occurrence counts per PII type-pair (base-model rate)."""
    n = len(docs)
    inv = defaultdict(set)
    for i, d in enumerate(docs):
        for v in d:
            inv[v].add(i)
    # audited value pairs = distinct-type pairs present anywhere
    obs = defaultdict(float); npairs = defaultdict(int)
    values = list(inv.keys())
    # only consider values that have a known type
    typed = [v for v in values if type_of(v, text_to_type)]
    for v1, v2 in itertools.combinations(typed, 2):
        vt = valid_tuple((v1, v2), text_to_type)
        if vt is None:
            continue
        co = len(inv[v1] & inv[v2])
        if co > 0:
            obs["+".join(vt)] += co
            npairs["+".join(vt)] += 1
    return n, obs, npairs


def stage_analyze(dataset):
    out_dir = os.path.join(NULL_ROOT, dataset)
    fpath = os.path.join(out_dir, "filtered_labels.csv")
    if not os.path.isfile(fpath):
        fpath, _ = build_filtered_labels(dataset)

    text_to_type, all_tags, total_unique = load_type_maps(dataset)

    # tuple counts (comparable units) on BASE generations
    filt = analyze_filtered_texts(all_tags, fpath)
    unique_singles, uniq = set(), {2: set(), 3: set(), 4: set()}
    for fn, fd in filt.items():
        for item in fd["texts"]["single"]:
            if item and type_of(item, text_to_type):
                unique_singles.add(item)
        for name, n in (("pairs", 2), ("triples", 3), ("quadruples", 4)):
            for tup in fd["texts"][name]:
                if valid_tuple(tuple(tup), text_to_type):
                    uniq[n].add(tuple(sorted(tup)))

    docs = load_docs(fpath)
    n_docs, base_obs, base_npairs = cooccur_by_typepair(docs, text_to_type)

    # fine-tuned co-occurrence for comparison (from existing pipeline outputs)
    ft = {}
    ref = os.path.join(REPO, "reanalysis_results.json")
    if os.path.isfile(ref):
        rr = json.load(open(ref))
        for eps in ("nodp", "8eps", "4eps"):
            key = f"{dataset}-{eps}"
            if key in rr:
                ft[eps] = {r["type_pair"]: (r["observed_cooccur_docs"],
                                            r["n_synthetic_docs"] if "n_synthetic_docs" in r else None)
                           for r in rr[key]["null_model_by_typepair"]}
                ft[eps]["_ndocs"] = rr[key]["n_synthetic_docs"]

    result = {
        "dataset": dataset,
        "base_model": BASE_MODEL,
        "n_base_docs": n_docs,
        "comparable_units_base": {
            "total_unique_pii": total_unique,
            "unique_singles": len(unique_singles),
            "unique_pairs": len(uniq[2]),
            "unique_triples": len(uniq[3]),
            "unique_quadruples": len(uniq[4]),
        },
        "base_cooccur_by_typepair": {
            k: {"observed_docs": round(v, 1),
                "rate_per_doc": round(v / n_docs, 5),
                "n_unique_value_pairs": base_npairs[k]}
            for k, v in sorted(base_obs.items(), key=lambda x: -x[1])
        },
        "finetuned_vs_base_enrichment": {},
    }

    # enrichment = finetuned_rate / base_rate per type-pair (generative null)
    print(f"\n{'='*74}\n{dataset}: BASE-MODEL generative null ({n_docs} docs)\n{'='*74}")
    print(f"{'type-pair':<34}{'base/doc':>10}{'ft(nodp)/doc':>14}{'enrich':>9}")
    for eps in ("nodp",):
        if eps not in ft:
            continue
        ftn = ft[eps]["_ndocs"]
        rows = {}
        for tp, base_v in base_obs.items():
            base_rate = base_v / n_docs
            ft_obs = ft[eps].get(tp, (0, None))[0]
            ft_rate = ft_obs / ftn
            enrich = (ft_rate / base_rate) if base_rate > 0 else None
            rows[tp] = {"base_rate": round(base_rate, 5),
                        "ft_rate": round(ft_rate, 5),
                        "ft_over_base": round(enrich, 2) if enrich else "inf(base=0)"}
        # also type-pairs present in ft but absent in base (pure memorization)
        for tp in ft[eps]:
            if tp == "_ndocs" or tp in rows:
                continue
            ft_obs = ft[eps][tp][0]
            rows[tp] = {"base_rate": 0.0,
                        "ft_rate": round(ft_obs / ftn, 5),
                        "ft_over_base": "inf(base=0)"}
        result["finetuned_vs_base_enrichment"][eps] = rows
        for tp, r in sorted(rows.items(),
                            key=lambda x: -(x[1]["ft_rate"])):
            print(f"{tp:<34}{r['base_rate']:>10}{r['ft_rate']:>14}{str(r['ft_over_base']):>9}")

    outp = os.path.join(out_dir, "null_generative_results.json")
    json.dump(result, open(outp, "w"), indent=2)
    print(f"\n[analyze] wrote {outp}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["generate", "analyze", "all"], required=True)
    ap.add_argument("--dataset", choices=["i2b2", "meddocan"], required=True)
    ap.add_argument("--num", type=int, default=1000)
    ap.add_argument("--batch", type=int, default=20)
    a = ap.parse_args()
    if a.stage in ("generate", "all"):
        stage_generate(a.dataset, a.num, a.batch)
    if a.stage in ("analyze", "all"):
        build_filtered_labels(a.dataset)
        stage_analyze(a.dataset)
