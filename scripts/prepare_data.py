#!/usr/bin/env python3
"""
Prepare the restricted corpora (run once, after obtaining the data; see DATA.md).

    python scripts/prepare_data.py --dataset i2b2 --xml-dir /path/to/all/i2b2-2014/xml
    python scripts/prepare_data.py --dataset meddocan --xml-dir /path/to/all/meddocan/xml

Copies the XML notes to data/{dataset}/original/ and derives from their <TAGS>:
  original_tags.csv  Filename,Tag Name,ID,Start,End,Text,Type,Comment (one row per span)
  all_labels.csv     text,TYPE (unique annotated values)
With --check, only compares the derived tables with those already in data/{dataset}/.
"""
import argparse
import csv
import io
import os
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dpleak import data  # noqa: E402


def derive(xml_dir: Path):
    tags, labels = [], {}
    for f in sorted(p for p in os.listdir(xml_dir) if p.endswith(".xml")):
        root = ET.parse(xml_dir / f, parser=ET.XMLParser(encoding="utf-8")).getroot()
        for t in root.find("TAGS"):
            a = t.attrib
            tags.append([f, t.tag, a.get("id", ""), a.get("start", ""), a.get("end", ""),
                         a.get("text", ""), a.get("TYPE", ""), a.get("comment", "")])
            labels.setdefault((a.get("text", ""), a.get("TYPE", "")), None)
    return tags, [list(k) for k in labels]


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)
        return [tuple(x) for x in r]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["i2b2", "meddocan"])
    ap.add_argument("--xml-dir", type=Path)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    out = data.DATA / a.dataset
    src = a.xml_dir or out / "original"
    tags, labels = derive(src)
    if a.check:
        ok_t = sorted(map(tuple, tags)) == sorted(rows(out / "original_tags.csv"))
        ok_l = set(map(tuple, labels)) == set(rows(out / "all_labels.csv"))
        print(f"{a.dataset}: original_tags {'OK' if ok_t else 'DIFF'} ({len(tags)} spans), "
              f"all_labels {'OK' if ok_l else 'DIFF'} ({len(labels)} values)")
        return
    (out / "original").mkdir(parents=True, exist_ok=True)
    for f in os.listdir(src):
        if f.endswith(".xml") and src != out / "original":
            shutil.copy(src / f, out / "original" / f)
    with open(out / "original_tags.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["Filename", "Tag Name", "ID", "Start", "End", "Text", "Type", "Comment"])
        w.writerows(tags)
    with open(out / "all_labels.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["text", "TYPE"])
        w.writerows(labels)
    print(f"{a.dataset}: {len(os.listdir(out / 'original'))} notes, {len(tags)} spans, {len(labels)} values")


if __name__ == "__main__":
    main()
