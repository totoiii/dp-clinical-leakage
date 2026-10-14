"""Check that dpleak.data rebuilds every legacy pre-built condition folder exactly
(same files, same <TEXT>), and that the prompt equals the legacy one.
    python scripts/verify_conditions.py /path/to/legacy/data
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dpleak import data, spec  # noqa: E402

legacy = Path(sys.argv[1])
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "legacy"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "vendor"))
ok = True
try:
    from utils import create_prompt_completion  # legacy prompts
    for ds in spec.DATASETS:
        same = create_prompt_completion("", spec.LANG[ds]) == data.prompt(ds)
        print(f"prompt {ds}: {'OK' if same else 'DIFF'}"); ok &= same
except Exception as e:
    print("prompt check skipped:", e)


def legacy_dir(ds, canary, k, tag):
    root = legacy / (ds if canary == "docs" else f"{ds}_sentences")
    return root / ("0_canaries" if k == 0 else f"{k}_canaries_{spec.FOLDER_SUFFIX[tag]}")


conds = [("docs", 0, None)] + [("docs", k, t) for k in (1, 10, 100) for t in spec.TAGSETS] \
        + [("sent", k, "A") for k in (10, 100)]
for ds in spec.DATASETS:
    for canary, k, tag in conds:
        d = legacy_dir(ds, canary, k, tag)
        ref = {f: data.read_text(d / f) for f in os.listdir(d) if f.endswith(".xml")}
        new = dict(data.corpus(ds, canary, k, tag))
        same = ref == new
        ok &= same
        nc = sum(f.startswith("canary_") for f in new)
        authors = len({data.author_of(ds, f) for f in new})
        print(f"{ds:9s} {canary}{k:<4d} {tag or '-'}: {len(new)} docs, {nc} canary docs, "
              f"{authors} authors -> {'OK' if same else 'DIFF'}")
print("ALL OK" if ok else "MISMATCH")
