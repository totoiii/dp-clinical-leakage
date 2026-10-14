#!/usr/bin/env python3
"""Apples-to-apples: apply the SAME co-occurrence function to base vs fine-tuned
i2b2 filtered_labels, per-doc normalized. Also report single-value 'leakage' to
expose substring-matching false positives."""
import os, csv, ast, itertools
from collections import defaultdict
csv.field_size_limit(10**7)
REPO=os.path.dirname(os.path.abspath(__file__))
EXCL={"SEXO_SUJETO_ASISTENCIA"}

def type_maps(ds):
    m={}
    with open(f"{REPO}/data/{ds}/original_tags.csv",encoding="utf-8") as f:
        r=csv.reader(f);next(r)
        for row in r:
            if len(row)>5 and row[5] and row[1]:
                m[row[5].lower()]=row[1]
    return m
def tof(t,m): return m.get(t.lower())
def vtup(items,m):
    if len(items)!=len(set(items)):return None
    ts=[tof(x,m) for x in items]
    if None in ts or len(ts)!=len(set(ts)):return None
    if any(t in EXCL for t in ts):return None
    return tuple(sorted(ts))
def load(fp):
    docs=[]
    with open(fp,encoding="utf-8") as f:
        for row in csv.reader(f):
            if len(row)>=2:
                try:docs.append(set(ast.literal_eval(row[1].strip())))
                except:pass
    return docs
def rates(docs,m):
    n=len(docs); inv=defaultdict(set)
    for i,d in enumerate(docs):
        for v in d: inv[v].add(i)
    typed=[v for v in inv if tof(v,m)]
    obs=defaultdict(float)
    # singles per type
    single=defaultdict(int)
    for v in typed:
        single[tof(v,m)]+=len(inv[v])
    for v1,v2 in itertools.combinations(typed,2):
        vt=vtup((v1,v2),m)
        if vt is None:continue
        co=len(inv[v1]&inv[v2])
        if co>0: obs["+".join(vt)]+=co
    return n,obs,len(typed),single

ds="i2b2"; m=type_maps(ds)
base_n,base_obs,base_vals,base_single=rates(load(f"{REPO}/null_base/{ds}/filtered_labels.csv"),m)
ft_n,ft_obs,ft_vals,ft_single=rates(load(f"{REPO}/results/output/llama-1B-{ds}-0can-common-nodp/filtered_labels.csv"),m)
print(f"BASE  : {base_n} docs, {base_vals} distinct training-PII values matched (substring)")
print(f"FT nodp: {ft_n} docs, {ft_vals} distinct training-PII values matched")
print(f"\n{'type-pair':<26}{'base/doc':>10}{'ft/doc':>10}{'ft/base':>9}")
allk=set(base_obs)|set(ft_obs)
for k in sorted(allk,key=lambda x:-(ft_obs.get(x,0)/ft_n)):
    br=base_obs.get(k,0)/base_n; fr=ft_obs.get(k,0)/ft_n
    ratio=f"{fr/br:.2f}" if br>0 else "inf"
    print(f"{k:<26}{br:>10.3f}{fr:>10.3f}{ratio:>9}")
