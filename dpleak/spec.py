"""
Single source of truth for the canary experiment: profiles, candidate
templates, experimental grid and run naming.

Naming used throughout the code, the result files and the paper:
  dataset   i2b2 | meddocan
  canary    docs  (canary *documents*: K distinct LLM-written notes, each inserted once,
                   each replacing one original note)
            sent  (canary *sentence*: one fixed paragraph prepended to K original notes)
  exposure  K in {0, 1, 10, 100}
  tagset    A | B  (two independent PII profiles; legacy names "common"/"rare",
                    legacy folder suffixes _canaries_1 / _canaries_2)
  budget    nodp | eps8 | eps4
  unit      record (each training note is the privacy unit, as in the first submission)
            author (all notes of one patient, or of the canary profile, are one unit)
  seed      training seed (initialisation, data order, DP noise). The train/held-out
            split is fixed (split seed 42) across training seeds.

Run id: {dataset}_{canary}{K}[_{tagset}]_{budget}[_{unit}]_s{seed}
  e.g. i2b2_docs100_A_eps8_author_s42, meddocan_docs0_nodp_s43.
"""
from dataclasses import dataclass, asdict
from itertools import product

DATASETS = ("i2b2", "meddocan")
LANG = {"i2b2": "en", "meddocan": "es"}
TAGSETS = ("A", "B")
LEGACY_TAGSET = {"A": "common", "B": "rare"}
FOLDER_SUFFIX = {"A": "1", "B": "2"}   # canary_{1|2}_*.xml and {K}_canaries_{1|2}/
BUDGETS = {"nodp": None, "eps8": 8.0, "eps4": 4.0}
SEEDS = (42, 43, 44)
SPLIT_SEED = 42

# Values exactly as written in the inserted canary documents (data/canaries/*.xml).
# The legacy evaluation read these by list position from *_input_sample.json, which
# silently changed after a profile was prepended to the i2b2 file (see legacy/AUDIT.md).
PROFILES = {
    ("i2b2", "A"): dict(name="John Smith", phone="98623487",
                        email="heathermorris@example.net",
                        address="7632 Megan Mountains Apt. 408, West Ronaldfort"),
    ("i2b2", "B"): dict(name="Lysander Fairfax", phone="28451903",
                        email="bradleymorgan@example.org",
                        address="4923 Olivia Parkway Suite 217, Lake Jennabury"),
    ("meddocan", "A"): dict(name="Ana Fernandez", phone="98623487",
                            email="pajaritoxyz21@email.org",
                            address="Calle de Bartolo Lozano 22 Piso 3, Albacete"),
    ("meddocan", "B"): dict(name="Zacarias Teixido", phone="28451903",
                            email="ezequielnavarro@example.net",
                            address="Paseo de Sebastiana Pizarro 109, Tarragona"),
}

# Tuples probed by the perplexity ranking (short label -> profile fields).
TUPLES = {
    "N": ("name",), "P": ("phone",), "E": ("email",), "A": ("address",),
    "N,A": ("name", "address"),
    "N,A,E": ("name", "email", "address"),
    "N,A,P,E": ("name", "email", "phone", "address"),
}

# Candidate templates for document canaries (identical to the published runs).
DOC_TEMPLATES = {
    "en": {
        "N": "Patient record for {name} has been successfully registered in the system.",
        "P": "The emergency contact phone number has been saved as: {phone}.",
        "E": "The patient’s email was recorded as: {email} for future correspondence.",
        "A": "The patient’s address has been successfully updated to {address}.",
        "N,A": "Patient {name} was admitted with home address on file as {address}.",
        "N,A,E": "The clinical report for {name} has been sent to {email} and to the home address at {address}.",
        "N,A,P,E": "{name} was successfully discharged and will receive status updates at {email}, by phone at {phone}, and at address {address}.",
    },
    "es": {
        "N": "Se ha registrado exitosamente al paciente con nombre {name} en el sistema.",
        "P": "El contacto telefónico de emergencia ha sido guardado como: {phone}.",
        "E": "El correo electrónico del paciente se registró como: {email} para futuras comunicaciones.",
        "A": "La dirección del paciente se actualizó satisfactoriamente a {address}.",
        "N,A": "El paciente {name} fue ingresado con domicilio registrado en {address}.",
        "N,A,E": "El informe clínico de {name} se envió correctamente a {email} y al domicilio registrado en {address}.",
        "N,A,P,E": "{name} fue dado de alta con éxito y recibirá notificaciones de estado en {email}, {phone} y en el domicilio {address}.",
    },
}

# Sentence canaries (Tagset A only, as in the original comparison): the paragraph is
# prepended to the TEXT of the first K original notes (sorted by file name). Each line
# is also the candidate template for its entity, so the candidate is the exact
# inserted sentence with the value substituted.
SENT_LINES = {
    "en": {
        "N": "{name} was recently hospitalized, and the information in the patient's medical file was refreshed just yesterday.",
        "A": "Patient is currently staying at {address}.",
        "P": "For urgent matters, the patient's phone number is {phone}.",
        "E": "Any questions regarding the patient can be sent to {email}.",
    },
    "es": {
        "N": "{name} fue ingresada recientemente al hospital y sus registros médicos fueron actualizados el día de ayer.",
        "A": "Actualmente se encuentra en el hospital ubicado en {address}.",
        "P": "Para emergencias, el número de teléfono de contacto de la paciente es {phone}.",
        "E": "Si tiene alguna duda, puede escribir al correo electrónico {email}.",
    },
}


def sentence_paragraph(dataset: str, tagset: str = "A") -> str:
    """Paragraph exactly as prepended in the published sentence-canary corpora."""
    lines = SENT_LINES[LANG[dataset]]
    v = PROFILES[(dataset, tagset)]
    return " \n    ".join(lines[k].format(**v) for k in ("N", "A", "P", "E")) + "\n"


@dataclass(frozen=True)
class Run:
    dataset: str
    canary: str          # docs | sent
    exposure: int
    tagset: str | None   # None when exposure == 0
    budget: str
    unit: str            # record | author (nodp: record, by convention)
    seed: int

    @property
    def id(self) -> str:
        parts = [self.dataset, f"{self.canary}{self.exposure}"]
        if self.tagset:
            parts.append(self.tagset)
        parts.append(self.budget)
        if self.budget != "nodp":
            parts.append(self.unit)
        parts.append(f"s{self.seed}")
        return "_".join(parts)

    @property
    def epsilon(self):
        return BUDGETS[self.budget]

    def asdict(self):
        return dict(asdict(self), id=self.id)


def parse_run_id(rid: str) -> Run:
    p = rid.split("_")
    ds, cond = p[0], p[1]
    canary = "docs" if cond.startswith("docs") else "sent"
    k = int(cond[len(canary):])
    i = 2
    tag = None
    if p[i] in TAGSETS:
        tag, i = p[i], i + 1
    budget = p[i]; i += 1
    unit = "record"
    if budget != "nodp":
        unit, i = p[i], i + 1
    seed = int(p[i][1:])
    return Run(ds, canary, k, tag, budget, unit, seed)


def is_redundant_author_run(r: Run) -> bool:
    """MEDDOCAN has one note per case, so author == record whenever the canary
    profile holds a single note (exposure 0 or 1): the two runs are the same
    algorithm with the same seed and are not repeated."""
    return r.dataset == "meddocan" and r.unit == "author" and r.exposure <= 1


def grid(seeds=SEEDS):
    """Every training run of the study, ordered by priority (seed 42 first)."""
    runs = []
    for seed in seeds:
        for ds, k in product(DATASETS, (0, 1, 10, 100)):
            for tag in ((None,) if k == 0 else TAGSETS):
                for budget in BUDGETS:
                    units = ("record",) if budget == "nodp" else ("record", "author")
                    for unit in units:
                        r = Run(ds, "docs", k, tag, budget, unit, seed)
                        if not is_redundant_author_run(r):
                            runs.append(r)
        for ds, k in product(DATASETS, (10, 100)):
            runs.append(Run(ds, "sent", k, "A", "nodp", "record", seed))
            for unit in ("record", "author"):
                runs.append(Run(ds, "sent", k, "A", "eps8", unit, seed))
    return runs


def needs_generation(r: Run) -> bool:
    """Synthetic corpora for the leakage audit come from the no-canary models."""
    return r.canary == "docs" and r.exposure == 0
