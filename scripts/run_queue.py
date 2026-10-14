#!/usr/bin/env python3
"""
GPU job queue for the whole study (resumable; safe to kill and restart).

    nohup setsid python scripts/run_queue.py --gpus 0,1,2 > runs/queue.out 2>&1 &

Each job is a sequence of stages; a stage is skipped when its output exists:
    train     -> runs/{id}/run.json
    score     -> runs/{id}/ranks.json
    generate  -> runs/{id}/generation.json            (no-canary models only)
    base      -> runs/base/{ds}_g{seed}/generation.json
    legacy    -> results/legacy_rescore/{name}.json   (re-score of the published adapters)
A job starts on a GPU only if that GPU has at least --min-free-gb free memory, so the
queue coexists with other users of the server. Failed jobs are retried (--retries).
Status: runs/queue_status.json; per-job logs: runs/logs/{job}.log
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from dpleak import spec  # noqa: E402

PY = sys.executable
LEGACY_OUT = os.environ.get("DPLEAK_LEGACY_OUT", str(Path.home() / "Repos/emnlp_2026/results/output"))


def free_mb(gpu):
    out = subprocess.check_output(
        ["nvidia-smi", "-i", str(gpu), "--query-gpu=memory.total,memory.used", "--format=csv,noheader,nounits"],
        text=True, env={**os.environ, "CUDA_DEVICE_ORDER": "PCI_BUS_ID"})
    tot, used = map(int, out.strip().split(","))
    return tot - used


def dpleak_procs():
    """{pid: cmdline} of every dpleak process on this machine (also those started by an
    earlier queue instance, so a restarted queue does not launch duplicates)."""
    out = {}
    for d in Path("/proc").iterdir():
        if d.name.isdigit():
            try:
                c = (d / "cmdline").read_bytes().replace(b"\0", b" ").decode()
            except OSError:
                continue
            if "dpleak." in c and "bash -c" not in c:
                out[int(d.name)] = c
    return out


def ours_per_gpu(procs):
    """Number of our processes on each GPU index (PCI order), from nvidia-smi."""
    env = {**os.environ, "CUDA_DEVICE_ORDER": "PCI_BUS_ID"}
    uuids = subprocess.check_output(["nvidia-smi", "--query-gpu=index,uuid", "--format=csv,noheader"],
                                    text=True, env=env)
    idx = {u.strip(): int(i) for i, u in (l.split(",") for l in uuids.strip().splitlines())}
    apps = subprocess.check_output(["nvidia-smi", "--query-compute-apps=gpu_uuid,pid", "--format=csv,noheader"],
                                   text=True, env=env)
    n = {}
    for line in apps.strip().splitlines():
        if not line.strip():
            continue
        u, pid = (x.strip() for x in line.split(","))
        if int(pid) in procs:
            n[idx[u]] = n.get(idx[u], 0) + 1
    return n


def jobs(runs_dir: Path):
    """Ordered job list: seed 42 grid, base corpora, legacy re-score, seeds 43 and 44."""
    out = []

    def run_job(r):
        stages = [("train", runs_dir / r.id / "run.json",
                   [PY, "-m", "dpleak.train", "--run", r.id, "--runs-dir", str(runs_dir),
                    "--per-device-batch", "4"]),
                  ("score", runs_dir / r.id / "ranks.json",
                   [PY, "-m", "dpleak.score", "--run", r.id, "--runs-dir", str(runs_dir)])]
        if spec.needs_generation(r):
            stages.append(("generate", runs_dir / r.id / "generation.json",
                           [PY, "-m", "dpleak.generate", "--run", r.id, "--runs-dir", str(runs_dir)]))
        return dict(name=r.id, stages=stages)

    by_seed = {s: [r for r in spec.grid((s,))] for s in spec.SEEDS}
    out += [run_job(r) for r in by_seed[42]]
    for ds in spec.DATASETS:
        for g in (1, 2, 3):
            d = runs_dir / "base" / f"{ds}_g{g}"
            out.append(dict(name=f"base_{ds}_g{g}", stages=[(
                "base", d / "generation.json",
                [PY, "-m", "dpleak.generate", "--base", ds, "--gen-seed", str(g), "--runs-dir", str(runs_dir)])]))
    legacy = Path(LEGACY_OUT)
    if legacy.is_dir():
        for a in sorted(legacy.glob("llama-1B-*")):
            n = a.name
            if not (a / "adapter_model.safetensors").exists():
                continue
            ds = "meddocan" if "meddocan" in n else "i2b2" if "i2b2" in n else None
            if ds is None:
                continue
            canary = "sent" if "_sentences" in n else "docs"
            o = REPO / "results" / "legacy_rescore" / f"{n}.json"
            out.append(dict(name=f"legacy_{n}", stages=[(
                "legacy", o, [PY, "-m", "dpleak.score", "--adapter", str(a), "--dataset", ds,
                              "--canary", canary, "--out", str(o)])]))
    for s in (43, 44):
        out += [run_job(r) for r in by_seed[s]]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpus", default="0,1,2")
    ap.add_argument("--runs-dir", default=str(REPO / "runs"))
    ap.add_argument("--min-free-gb", type=float, default=15)
    ap.add_argument("--max-per-gpu", type=int, default=1)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--poll", type=int, default=30)
    a = ap.parse_args()
    runs_dir = Path(a.runs_dir)
    (runs_dir / "logs").mkdir(parents=True, exist_ok=True)
    gpus = [int(g) for g in a.gpus.split(",")]
    running = {}            # job name -> (Popen, gpu, stage_idx)
    attempts = {}
    started_at = {}
    while True:
        pause = (runs_dir / "PAUSE").exists()
        # runs/MAX_PER_GPU: "2" (all GPUs) or "0:1,1:2,2:1" (per GPU), re-read every poll
        limits = {g: a.max_per_gpu for g in gpus}
        try:
            txt = (runs_dir / "MAX_PER_GPU").read_text().strip()
            if ":" in txt:
                limits.update({int(k): int(v) for k, v in (x.split(":") for x in txt.split(","))})
            else:
                limits = {g: int(txt) for g in gpus}
        except (OSError, ValueError):
            pass
        procs = dpleak_procs()
        external = " ".join(procs.values())
        all_jobs = jobs(runs_dir)
        pending = []
        for j in all_jobs:
            todo = [i for i, (_, out, _) in enumerate(j["stages"]) if not Path(out).exists()]
            busy = j["name"] in running or any(
                f" {j['name']} " in f" {c} " or f"/{j['name'].removeprefix('legacy_')} " in f"{c} "
                for c in procs.values())
            if todo and not busy and attempts.get(j["name"], 0) < a.retries:
                pending.append(j)
        # reap
        for name, (p, gpu, _) in list(running.items()):
            if p.poll() is not None:
                ok = p.returncode == 0
                if not ok:
                    attempts[name] = attempts.get(name, 0) + 1
                print(f"{time.strftime('%F %T')} {'END ' if ok else 'FAIL'} {name} gpu{gpu} "
                      f"rc={p.returncode} {time.time() - started_at[name]:.0f}s", flush=True)
                del running[name]
        # launch
        if not pause:
            for gpu in gpus:
                ours = max(sum(1 for _, g, _ in running.values() if g == gpu),
                           ours_per_gpu(dpleak_procs()).get(gpu, 0))
                if ours >= limits.get(gpu, a.max_per_gpu) or not pending:
                    continue
                if free_mb(gpu) < a.min_free_gb * 1024:
                    continue
                j = pending.pop(0)
                stages = [s for s in j["stages"] if not Path(s[1]).exists()]
                cmd = " && ".join(" ".join(f"'{c}'" for c in s[2]) for s in stages)
                env = {**os.environ, "CUDA_DEVICE_ORDER": "PCI_BUS_ID", "CUDA_VISIBLE_DEVICES": str(gpu),
                       "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True", "PYTHONUNBUFFERED": "1"}
                log = open(runs_dir / "logs" / f"{j['name']}.log", "a")
                log.write(f"\n===== {time.strftime('%F %T')} gpu{gpu} attempt {attempts.get(j['name'], 0) + 1}\n{cmd}\n")
                log.flush()
                p = subprocess.Popen(["bash", "-c", cmd], cwd=REPO, env=env, stdout=log, stderr=subprocess.STDOUT)
                running[j["name"]] = (p, gpu, 0)
                started_at[j["name"]] = time.time()
                print(f"{time.strftime('%F %T')} START {j['name']} gpu{gpu} stages={[s[0] for s in stages]}", flush=True)
                time.sleep(20)   # let the model load before measuring memory again
        done = sum(1 for j in all_jobs if all(Path(o).exists() for _, o, _ in j["stages"]))
        failed = [n for n, k in attempts.items() if k >= a.retries]
        status = dict(time=time.strftime("%F %T"), total=len(all_jobs), done=done,
                      running={n: g for n, (_, g, _) in running.items()},
                      pending=len(pending), failed=failed, paused=pause)
        (runs_dir / "queue_status.json").write_text(json.dumps(status, indent=1))
        if not running and not pending and not procs:
            print(f"{time.strftime('%F %T')} queue empty; done={done}/{len(all_jobs)} failed={failed}", flush=True)
            break
        time.sleep(a.poll)


if __name__ == "__main__":
    main()
