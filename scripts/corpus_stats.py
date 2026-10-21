#!/usr/bin/env python3
"""
Corpus statistics of the two annotated corpora (Table 1 of the manuscript).

    python scripts/corpus_stats.py        # writes results/corpus_stats.json

Reads the restricted corpora (data/{dataset}/original/*.xml and original_tags.csv) and
writes counts only. Definitions:
  word tokens     maximal runs of Unicode word characters (regex \\w+) in the <TEXT> of a note
  vocabulary      distinct lower-cased word tokens
  PII types       distinct annotation types (column Type of original_tags.csv)
  PII instances   annotated spans
  PII token ratio word tokens inside annotated spans / all word tokens (spans do not overlap)
"""
import csv
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dpleak import data, spec  # noqa: E402

WORD = re.compile(r"\w+")


def stats(ds):
    folder = data.DATA / ds / "original"
    texts = []
    for f in sorted(p for p in os.listdir(folder) if p.endswith(".xml")):
        root = ET.parse(folder / f, parser=ET.XMLParser(encoding="utf-8")).getroot()
        texts.append(root.find("TEXT").text or "")
    words = [w for t in texts for w in WORD.findall(t)]
    with open(data.DATA / ds / "original_tags.csv", newline="", encoding="utf-8") as fh:
        spans = [r for r in csv.DictReader(fh) if r["Text"]]
    pii_words = sum(len(WORD.findall(r["Text"])) for r in spans)
    return dict(documents=len(texts), word_tokens=len(words), vocabulary=len({w.lower() for w in words}),
                word_tokens_per_doc=len(words) / len(texts), pii_types=len({r["Type"] for r in spans}),
                pii_instances=len(spans), pii_instances_per_doc=len(spans) / len(texts),
                pii_token_ratio=pii_words / len(words))


def main():
    out = {ds: stats(ds) for ds in spec.DATASETS}
    path = Path(__file__).resolve().parent.parent / "results" / "corpus_stats.json"
    path.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
