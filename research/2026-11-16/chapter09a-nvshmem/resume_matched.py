from pathlib import Path
from datetime import datetime, timezone
import argparse
import subprocess
import os
import re
import math

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
LOGROOT = ROOT / "logs"

ORIGINAL = (
    LOGROOT / "run_job2939543_20261116T145816Z"
)

MODES = {
    "A": ("nvshmem_device_scalar", "32x32", []),
    "B": ("nvshmem_device_scalar_1d", "32x32",
          ["-scalar_1d"]),
    "C": ("nvshmem_device_scalar_1d", "256x1",
          ["-scalar_1d", "-ref_1d"]),
    "D": ("nvshmem_device_block", "256x1",
          ["-use_block_comm", "-ref_1d"]),
}

ORDERS = [
    "ABDC", "BCAD", "CDBA", "DACB",
    "CDBA", "DACB", "ABDC", "BCAD"
]

PLAN = [
    (config, nc, rep)
    for rep, order in enumerate(ORDERS, 1)
    for nc in ([1, 10] if rep % 2 else [10, 1])
    for config in order
]

parser = argparse.ArgumentParser()
parser.add_argument("--run", action="store_true")
parser.add_argument("--max-new", type=int, default=8)
args = parser.parse_args()


def filename(case):
    config, nc, rep = case
    return f"bench_{config}_nc{nc}_r{rep}.log"


def valid_log(path, case, require_marker=True):
    if not path.is_file():
        return False

    # Original runs predate .ok markers.
    # All resumed runs must have a completion marker.
    if require_marker and path.parent != ORIGINAL:
        if not Path(str(path) + ".ok").is_file():
            return False

    s = path.read_text(errors="replace")

    if re.search(r"ERROR: CUDA|ERROR: MPI|srun: error:", s):
        return False

    checks = [
        line for line in s.splitlines()
        if line.startswith("STRICT_VALIDATION:")
    ]

    if len(checks) != 1:
        return False

    if not checks[0].startswith("STRICT_VALIDATION: PASS "):
        return False

    try:
        v = dict(
            x.split("=", 1)
            for x in checks[0].split()[2:]
        )

        for k, expected in {
            "checked": 268369924,
            "expected": 268369924,
            "nonfinite": 0,
            "mismatches": 0,
            "ref_iters": 1000,
            "multi_iters": 1000,
        }.items():
            if int(v[k]) != expected:
                return False

        results = [
            line for line in s.splitlines()
            if line.startswith("MATCHED_RESULT:")
        ]

        if len(results) != 1:
            return False

        d = dict(
            x.split("=", 1)
            for x in results[0].split()[1:]
        )

        config, nc, rep = case
        method, ref, _ = MODES[config]

        expected = {
            "method": method,
            "ref": ref,
            "nx": "16384",
            "ny": "16384",
            "iter": "1000",
            "nc": str(nc),
            "pes": "4",
        }

        if not all(d.get(k) == x for k, x in expected.items()):
            return False

        for k in ("ref_sec", "ref_max_sec", "parallel_sec"):
            t = float(d[k])
            if not math.isfinite(t) or t <= 0:
                return False

    except (KeyError, ValueError):
        return False

    return True


def scan():
    complete = {}
    missing = []
    extras = 0

    for case in PLAN:
        paths = sorted(
            LOGROOT.glob(f"run_job*/{filename(case)}")
        )

        good = [p for p in paths if valid_log(p, case)]

        if good:
            complete[case] = good
            extras += len(good) - 1
        else:
            missing.append(case)

    print("\n=== MATCHED GEOMETRY INVENTORY ===")
    print(f"Completed unique cases: {len(complete)}/64")
    print(f"Extra valid repeats:    {extras}")
    print(f"Missing cases:          {len(missing)}")

    print("\nRound    Completed / 8")

    for rep in range(1, 9):
        n = sum(case[2] == rep for case in complete)
        print(f"{rep:5d}    {n}/8")

    print("\n=== MISSING CASES ===")
    for case in missing:
        print(filename(case))

    return complete, missing


def slurm_state(job):
    output = subprocess.check_output(
        ["squeue", "-h", "-j", job, "-o", "%T|%L|%N"],
        text=True
    ).strip()

    if not output:
        raise SystemExit("Allocation is no longer active.")

    state, left, node = output.split("|", 2)

    if state != "RUNNING":
        raise SystemExit(f"Allocation state: {state}")

    # Slurm time formats: MM:SS, HH:MM:SS, D-HH:MM:SS.
    days = 0
    if "-" in left:
        days, left = left.split("-", 1)
        days = int(days)

    seconds = 0
    for part in left.split(":"):
        seconds = seconds * 60 + int(part)

    return days * 86400 + seconds, node


complete, missing = scan()

if not args.run or not missing:
    raise SystemExit(0)

job = os.environ.get("SLURM_JOB_ID")
if not job:
    raise SystemExit("No active Slurm allocation.")

subprocess.run(
    ["sha256sum", "-c", "../build.sha256"],
    cwd=WORK, check=True
)

remaining, node = slurm_state(job)

stamp = datetime.now(timezone.utc).strftime(
    "%Y%m%dT%H%M%S%fZ"
)

logdir = LOGROOT / f"run_job{job}_{stamp}"
logdir.mkdir()

with (logdir / "allocation.txt").open("w") as f:
    subprocess.run(
        ["scontrol", "-o", "show", "job", job],
        stdout=f, check=True
    )

env = os.environ.copy()
env["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"

new_runs = 0

for case in missing:

    if new_runs >= args.max_new:
        break

    remaining, node = slurm_state(job)

    if remaining < 90:
        print("Stopping safely: less than 90 seconds left.")
        break

    config, nc, rep = case
    method, ref, flags = MODES[config]
    path = logdir / filename(case)

    print(f"\n=== {filename(case)} ===", flush=True)
    print(f"Job {job}, Node {node}, {remaining}s left",
          flush=True)

    cmd = [
        "srun",
        "--cpu-bind=verbose,sockets",
        "--unbuffered",
        "--kill-on-bad-exit=1",
        "-n", "4",
        str(WORK / "jacobi"),
        "-nx", "16384",
        "-ny", "16384",
        "-niter", "1000",
        "-nccheck", str(nc),
        *flags
    ]

    with path.open("w") as f:
        f.write(f"Job: {job}\nNode: {node}\n")
        f.flush()

        proc = subprocess.Popen(
            cmd,
            cwd=WORK,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in proc.stdout:
            print(line, end="", flush=True)
            f.write(line)
            f.flush()

        rc = proc.wait()

    if rc != 0 or not valid_log(
        path, case, require_marker=False
    ):
        print(f"FAILED OR INCOMPLETE: {path}")
        raise SystemExit(1)

    Path(str(path) + ".ok").touch()

    new_runs += 1
    print(f"New runs completed: {new_runs}",
          flush=True)

print("\n=== BATCH COMPLETE ===")
print(f"New runs: {new_runs}")
print(f"Logs: {logdir}")

scan()
