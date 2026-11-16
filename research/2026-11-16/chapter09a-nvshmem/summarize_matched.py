# Copyright IoriOikawa, 2026

from pathlib import Path
from collections import defaultdict
from statistics import median
from datetime import datetime, timezone
import csv
import re
import math

# ============================================================
# 1. Discover all experiment directories
# ============================================================

ROOT = Path.cwd().resolve().parent
LOGROOT = ROOT / "logs"

ORIGINAL = (
    LOGROOT / "run_job2939543_20261116T145816Z"
)

assert LOGROOT.is_dir(), f"Missing log directory: {LOGROOT}"

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUT = ROOT / "summary" / STAMP
OUT.mkdir(parents=True, exist_ok=False)

pattern = re.compile(
    r"bench_([ABCD])_nc(\d+)_r(\d+)\.log$"
)

expected_modes = {
    "A": ("nvshmem_device_scalar", "32x32"),
    "B": ("nvshmem_device_scalar_1d", "32x32"),
    "C": ("nvshmem_device_scalar_1d", "256x1"),
    "D": ("nvshmem_device_block", "256x1"),
}

expected_cases = {
    (config, nc, rep)
    for config in "ABCD"
    for nc in (1, 10)
    for rep in range(1, 9)
}

all_rows = []
rejected = []

# ============================================================
# 2. Validate and parse each benchmark log
# ============================================================

def parse_log(p, config, nc, rep):

    # Original benchmark predates completion markers.
    # All resumed runs must have an .ok marker.
    if p.parent != ORIGINAL:
        if not Path(str(p) + ".ok").is_file():
            raise ValueError("Missing completion marker")

    s = p.read_text(errors="replace")
    lines = s.splitlines()

    if re.search(
        r"ERROR: CUDA|ERROR: MPI|srun: error:",
        s
    ):
        raise ValueError("Runtime error in log")

    checks = [
        x for x in lines
        if x.startswith("STRICT_VALIDATION:")
    ]

    results = [
        x for x in lines
        if x.startswith("MATCHED_RESULT:")
    ]

    if len(checks) != 1 or len(results) != 1:
        raise ValueError("Missing or duplicate result")

    if not checks[0].startswith("STRICT_VALIDATION: PASS "):
        raise ValueError("Strict validation failed")

    v = dict(
        x.split("=", 1)
        for x in checks[0].split()[2:]
    )

    expected_validation = {
        "checked": 268369924,
        "expected": 268369924,
        "nonfinite": 0,
        "mismatches": 0,
        "ref_iters": 1000,
        "multi_iters": 1000,
    }

    for k, expected in expected_validation.items():
        if int(v[k]) != expected:
            raise ValueError(f"Invalid validation field: {k}")

    error = float(v["max_abs_error"])
    tol = float(v["tol"])

    if (
        not math.isfinite(error)
        or not math.isfinite(tol)
        or tol <= 0
        or error < 0
        or error > tol
    ):
        raise ValueError("Invalid numerical error")

    data = dict(
        x.split("=", 1)
        for x in results[0].split()[1:]
    )

    method, ref = expected_modes[config]

    expected_result = {
        "method": method,
        "ref": ref,
        "nc": str(nc),
        "pes": "4",
        "iter": "1000",
        "nx": "16384",
        "ny": "16384",
    }

    for k, expected in expected_result.items():
        if data.get(k) != expected:
            raise ValueError(f"Invalid result field: {k}")

    timings = {}

    for k in (
        "ref_sec",
        "ref_max_sec",
        "parallel_sec",
        "speedup",
        "efficiency",
    ):
        t = float(data[k])

        if not math.isfinite(t) or t <= 0:
            raise ValueError(f"Invalid timing: {k}")

        timings[k] = t

    job_match = re.search(
        r"^Job:\s*(\S+)", s, re.MULTILINE
    )

    node_match = re.search(
        r"^Node:\s*(\S+)", s, re.MULTILINE
    )

    if not job_match or not node_match:
        raise ValueError("Missing job or node metadata")

    job = job_match.group(1)
    node = node_match.group(1)

    if not p.parent.name.startswith(f"run_job{job}_"):
        raise ValueError("Job ID does not match directory")

    return {
        "config": config,
        "nc": nc,
        "rep": rep,
        "method": method,
        "ref_geometry": ref,
        "job_id": job,
        "node": node,
        "run_dir": p.parent.name,
        "log_path": str(p.relative_to(ROOT)),
        **timings,
        "checked": int(v["checked"]),
        "nonfinite": int(v["nonfinite"]),
        "mismatches": int(v["mismatches"]),
        "max_abs_error": error,
        "ref_iters": int(v["ref_iters"]),
        "multi_iters": int(v["multi_iters"]),
        "validation": "PASS",
    }


# Scan every allocation, not current_run_dir.txt.
for p in sorted(LOGROOT.glob("run_job*/bench_*.log")):

    m = pattern.fullmatch(p.name)

    if not m:
        continue

    config, nc, rep = m.groups()
    nc, rep = int(nc), int(rep)

    case = (config, nc, rep)

    if case not in expected_cases:
        rejected.append({
            "log_path": str(p.relative_to(ROOT)),
            "reason": "Outside planned experiment",
        })
        continue

    try:
        row = parse_log(p, config, nc, rep)
        all_rows.append(row)

    except (ValueError, KeyError, OSError) as e:
        rejected.append({
            "log_path": str(p.relative_to(ROOT)),
            "reason": str(e),
        })

# ============================================================
# 3. Separate primary results and extra repetitions
# ============================================================

by_case = defaultdict(list)

for row in all_rows:
    key = (row["config"], row["nc"], row["rep"])
    by_case[key].append(row)

primary_rows = []
extra_rows = []

for key in sorted(by_case):

    candidates = by_case[key]

    # Predefined selection rule:
    # original experiment first; otherwise earliest valid run.
    candidates.sort(
        key=lambda r: (
            r["run_dir"] != ORIGINAL.name,
            r["run_dir"].split("_", 2)[-1],
            r["job_id"],
        )
    )

    candidates[0]["sample_type"] = "primary"
    primary_rows.append(candidates[0])

    for r in candidates[1:]:
        r["sample_type"] = "extra"
        extra_rows.append(r)

missing = sorted(expected_cases - set(by_case))

# ============================================================
# 4. Export complete records
# ============================================================

fields = [
    "config", "nc", "rep", "sample_type",
    "method", "ref_geometry",
    "job_id", "node", "run_dir", "log_path",
    "ref_sec", "ref_max_sec", "parallel_sec",
    "speedup", "efficiency",
    "checked", "nonfinite", "mismatches",
    "max_abs_error", "ref_iters", "multi_iters",
    "validation",
]

def write_csv(name, rows, fieldnames):

    with (OUT / name).open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=fieldnames
        )
        writer.writeheader()
        writer.writerows(rows)

write_csv("benchmark_results.csv", primary_rows, fields)
write_csv("all_valid_results.csv", all_rows, fields)
write_csv("extra_repeats.csv", extra_rows, fields)

write_csv(
    "rejected_logs.csv",
    rejected,
    ["log_path", "reason"]
)

write_csv(
    "missing_cases.csv",
    [
        {"config": c, "nc": nc, "rep": rep}
        for c, nc, rep in missing
    ],
    ["config", "nc", "rep"]
)

# ============================================================
# 5. Inventory
# ============================================================

print("=== MATCHED GEOMETRY INVENTORY ===")
print(f"Unique planned cases: {len(primary_rows)}/64")
print(f"Extra valid repeats:  {len(extra_rows)}")
print(f"All valid samples:    {len(all_rows)}")
print(f"Missing cases:        {len(missing)}")
print(f"Rejected logs:        {len(rejected)}")

print()
print("=== COMPLETION BY ROUND ===")

for rep in range(1, 9):

    count = sum(
        r["rep"] == rep for r in primary_rows
    )

    print(f"Round {rep}: {count}/8")

if missing:
    print()
    print("WARNING: Dataset is still incomplete.")

    for config, nc, rep in missing:
        print(f"  bench_{config}_nc{nc}_r{rep}.log")

# ============================================================
# 6. Primary performance summary
# ============================================================

groups = defaultdict(list)

for row in primary_rows:
    groups[row["config"], row["nc"]].append(row)

print()
print("=== MATCHED GEOMETRY SUMMARY ===")
print()
print(
    f"{'NC':>3} {'Mode':>4} {'N':>3} "
    f"{'Ref median(s)':>15} "
    f"{'4GPU median(s)':>16} "
    f"{'Eff median(%)':>15} "
    f"{'Eff range(%)':>21}"
)

for nc in (1, 10):
    for config in "ABCD":

        g = groups[config, nc]

        if not g:
            continue

        ref = median(r["ref_sec"] for r in g)
        par = median(r["parallel_sec"] for r in g)
        eff = [r["efficiency"] for r in g]

        print(
            f"{nc:3d} {config:>4} {len(g):3d} "
            f"{ref:15.6f} {par:16.6f} "
            f"{median(eff):15.4f} "
            f"{min(eff):9.4f}--{max(eff):9.4f}"
        )

# ============================================================
# 7. Summary by allocation and node
# ============================================================

by_job = defaultdict(list)

for r in all_rows:
    key = (
        r["job_id"], r["node"],
        r["config"], r["nc"]
    )
    by_job[key].append(r)

job_summary = []

for (job, node, config, nc), g in sorted(by_job.items()):

    job_summary.append({
        "job_id": job,
        "node": node,
        "config": config,
        "nc": nc,
        "n": len(g),
        "ref_median_sec": median(
            r["ref_sec"] for r in g
        ),
        "parallel_median_sec": median(
            r["parallel_sec"] for r in g
        ),
        "efficiency_median": median(
            r["efficiency"] for r in g
        ),
    })

write_csv(
    "summary_by_allocation.csv",
    job_summary,
    [
        "job_id", "node", "config", "nc", "n",
        "ref_median_sec", "parallel_median_sec",
        "efficiency_median",
    ]
)

print()
print("=== JOB / NODE COVERAGE ===")

coverage = defaultdict(int)

for r in all_rows:
    coverage[r["job_id"], r["node"]] += 1

for (job, node), n in sorted(coverage.items()):
    print(f"Job {job} | {node} | {n} valid samples")

# ============================================================
# 8. B versus C: reference geometry effect
# ============================================================

print()
print("=== B vs C: Reference geometry effect ===")

for nc in (1, 10):

    b = groups["B", nc]
    c = groups["C", nc]

    if not b or not c:
        continue

    rb = median(r["ref_sec"] for r in b)
    rc = median(r["ref_sec"] for r in c)

    pb = median(r["parallel_sec"] for r in b)
    pc = median(r["parallel_sec"] for r in c)

    eb = median(r["efficiency"] for r in b)
    ec = median(r["efficiency"] for r in c)

    print(f"\nnc={nc}")
    print(f"  Samples B/C: {len(b)}/{len(c)}")
    print(f"  Reference 32x32: {rb:.6f} s")
    print(f"  Reference 256x1: {rc:.6f} s")
    print(
        f"  Reference time change: "
        f"{100*(rc/rb-1):+.3f}%"
    )
    print(
        f"  Parallel time change:  "
        f"{100*(pc/pb-1):+.3f}%"
    )
    print(f"  Old efficiency:     {eb:.4f}%")
    print(f"  Matched efficiency: {ec:.4f}%")
    print(f"  Difference: {ec-eb:+.4f} percentage points")

    # Only pair measurements within the same allocation/node.
    c_index = {
        (r["rep"], r["job_id"], r["node"]): r
        for r in c
    }

    pairs = [
        (r, c_index[(r["rep"], r["job_id"], r["node"])])
        for r in b
        if (r["rep"], r["job_id"], r["node"]) in c_index
    ]

    print(f"  Same-allocation paired samples: {len(pairs)}")

    if pairs:

        ref_changes = [
            100*(y["ref_sec"]/x["ref_sec"]-1)
            for x, y in pairs
        ]

        par_changes = [
            100*(y["parallel_sec"]/x["parallel_sec"]-1)
            for x, y in pairs
        ]

        print(
            f"  Paired median reference change: "
            f"{median(ref_changes):+.3f}%"
        )

        print(
            f"  Paired median parallel change:  "
            f"{median(par_changes):+.3f}%"
        )

# ============================================================
# 9. Final status
# ============================================================

print()
print("=== EXPORT COMPLETE ===")
print("Output directory:", OUT)

for p in sorted(OUT.glob("*.csv")):
    print(" ", p.name)

if len(primary_rows) == 64:
    print("\nALL 64 PLANNED BENCHMARKS COMPLETE.")
else:
    print("\nPARTIAL SUMMARY: more benchmarks required.")
