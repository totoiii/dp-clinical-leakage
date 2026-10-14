"""
Corpus construction for every experimental condition.

Restricted data (never committed) live under $DPLEAK_DATA (default: ./data):
    {dataset}/original/*.xml        the full annotated corpus (i2b2 2014: 1,304 notes;
                                    MEDDOCAN: 1,000 cases), XML with <TEXT> and <TAGS>
    {dataset}/original_tags.csv     one row per annotated PII span (see scripts/prepare_data.py)
    {dataset}/all_labels.csv        unique (text, TYPE) of the annotated spans

Synthetic, shareable inputs (committed):
    canaries/{dataset}/canary_{1|2}_{1..100}.xml   the 2 x 100 canary documents
    canaries/replacement_map.json                  which original notes each docs condition replaces

A docs condition with K documents replaces the K originals listed in the map by
canary_{tagset}_1..K, so the corpus size is constant. A sent condition prepends the
canary paragraph to the TEXT of the first K originals (sorted by file name).
"""
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path

from . import spec

REPO = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DPLEAK_DATA", REPO / "data"))
CANARIES = REPO / "canaries"
CANARY_AUTHOR = "__canary_profile__"

PROMPTS = {
    "en": (" Generate a hospital admission clinical report from scratch, ensuring medical accuracy, logical coherence, and consistency across all sections.\n"
           "                                                You must invent all the medical and patient information, but make sure it is coherent and realistic.\n"
           "                                                Medical report:\n"
           "                                                "),
    "es": (" Genera un reporte clinico desde cero de un ingreso hospitalario, asegurando precisión médica, coherencia logica y consistencia en todas las secciones.\n"
           "                        Debes inventar toda la información médica y del paciente, pero asegurate de que sea coherente y realista.\n"
           "                                                Reporte clinico:\n"
           "                                                "),
}


def prompt(dataset: str) -> str:
    """Fixed instruction prepended to every training note and used alone for generation
    (byte-identical to the prompt of the published runs)."""
    return PROMPTS[spec.LANG[dataset]]


def author_of(dataset: str, filename: str) -> str:
    """Privacy unit for author-level DP: the canary profile, the i2b2 patient
    (files are <patient>-<note>.xml), or the MEDDOCAN case (one file per case)."""
    stem = filename.rsplit(".", 1)[0]
    if stem.startswith("canary_"):
        return CANARY_AUTHOR
    if dataset == "i2b2":
        return stem.split("-")[0]
    return stem


def read_text(path: Path) -> str:
    root = ET.parse(path, parser=ET.XMLParser(encoding="utf-8")).getroot()
    return root.find("TEXT").text


def original_files(dataset: str) -> list[str]:
    d = DATA / dataset / "original"
    return sorted(f for f in os.listdir(d) if f.endswith(".xml"))


def replacement_map() -> dict:
    return json.loads((CANARIES / "replacement_map.json").read_text())


def corpus(dataset: str, canary: str = "docs", exposure: int = 0, tagset: str | None = None):
    """Return the training corpus of one condition as a list of (filename, text)."""
    files = original_files(dataset)
    odir = DATA / dataset / "original"
    if exposure == 0:
        return [(f, read_text(odir / f)) for f in files]
    if canary == "docs":
        suf = spec.FOLDER_SUFFIX[tagset]
        removed = set(replacement_map()[f"{dataset}/{exposure}_canaries_{suf}"]["removed_originals"])
        assert len(removed) == exposure
        docs = [(f, read_text(odir / f)) for f in files if f not in removed]
        cdir = CANARIES / dataset
        docs += [(f"canary_{suf}_{j}.xml", read_text(cdir / f"canary_{suf}_{j}.xml"))
                 for j in range(1, exposure + 1)]
        return sorted(docs)
    if canary == "sent":
        para = spec.sentence_paragraph(dataset, tagset or "A")
        out = []
        for i, f in enumerate(files):
            t = read_text(odir / f)
            out.append((f, para + t if i < exposure else t))
        return out
    raise ValueError(canary)


def training_split(dataset, canary="docs", exposure=0, tagset=None, split_seed=spec.SPLIT_SEED):
    """HF DatasetDict with columns text/author/file, split exactly like the published runs
    (train_test_split(test_size=0.001, shuffle=True, seed=42) on the file-sorted list)."""
    import datasets
    docs = corpus(dataset, canary, exposure, tagset)
    p = prompt(dataset)
    raw = datasets.Dataset.from_dict({
        "text": [p + t for _, t in docs],
        "author": [author_of(dataset, f) for f, _ in docs],
        "file": [f for f, _ in docs],
    })
    return raw.train_test_split(test_size=0.001, shuffle=True, seed=split_seed)
