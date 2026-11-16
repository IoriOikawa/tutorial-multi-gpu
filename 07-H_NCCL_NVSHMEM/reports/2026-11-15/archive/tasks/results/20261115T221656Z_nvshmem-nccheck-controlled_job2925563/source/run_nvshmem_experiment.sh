#!/usr/bin/env bash
# SC26 / JUPITER: controlled NVSHMEM Jacobi experiment.
# Run from the NVSHMEM source directory, inside a single-node Slurm allocation.
set -euo pipefail

: "${SLURM_JOB_ID:?Run inside salloc first (see instructions).}"
[[ -f jacobi.cu && -f Makefile ]] || { echo 'Run from the NVSHMEM source directory.' >&2; exit 2; }
export CUDA_VISIBLE_DEVICES=0,1,2,3
GPUS=4
NX=16384
NY=16384
NITER=1000
REPEATS=${REPEATS:-3}
PROFILE=${PROFILE:-0}
PROFILE_ITERS=${PROFILE_ITERS:-100}
CASE=nvshmem-nccheck-controlled
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
ROOT=$(realpath -m "${RESULT_ROOT:-../results}")
mkdir -p "$ROOT"
OUT="$ROOT/${STAMP}_${CASE}_job${SLURM_JOB_ID}"
mkdir "$OUT" # fail rather than overwrite a prior experiment
mkdir "$OUT"/{source,environment,logs,profiles}
OUT=$(realpath "$OUT")
printf 'Experiment directory: %s\n' "$OUT"

cat > "$OUT/README.md" <<NOTES
# $CASE

- Created (UTC): $STAMP
- Slurm allocation: $SLURM_JOB_ID
- Nodes: ${SLURM_JOB_NODELIST:-unknown}
- Method: NVSHMEM host-initiated Jacobi, overlap with quiet/event/barrier
- Mesh: ${NX} x ${NY}; ranks/GPUs: $GPUS; max iterations: $NITER
- Treatment: nccheck=1 vs 10; repetitions per treatment: $REPEATS
- CPU binding: sockets; one allocation, same executable, alternating order
- Profiling: $PROFILE (separate runs; $PROFILE_ITERS iterations if enabled)

## Background / question (recorded before execution)
SC26 tutorial, JUPITER, 2026-11-15. Earlier unprofiled runs:
- Job 2925255, nccheck=1, 4 GPUs: 0.4770 s (make run, sockets binding).
- Job 2925303, nccheck=10, 4 GPUs: 2.4381 s (manual srun; binding not recorded).
Earlier 10-iteration profile, job 2925292: 4 GPUs 0.0151 s;
PE0 showed overlapping Jacobi/PtoP activity and an unusually long barrier.
These observations are not controlled comparisons and do not establish a cause.

Question: does the slowdown recur when allocation, CPU binding, binary and
problem size are controlled? Alternative hypotheses: allocation/affinity or
system noise; host submission cadence; NVSHMEM barrier/progress effects.
No code-level ablation in this experiment. Profile runs are diagnostic only.

## Interpretation (fill after the run)
- Observations:
- Median and spread by nccheck:
- Unexpected events / failed runs:
- Conclusion and next experiment:

See runs.tsv, summary.txt, logs/, source/, environment/, profiles/.
NOTES
if [[ -n ${NOTE:-} ]]; then printf '\n## Additional pre-run note\n%s\n' "$NOTE" >> "$OUT/README.md"; fi

# Snapshot local build inputs, not prior results or personal environment.
find . -maxdepth 1 -type f \( -name '*.cu' -o -name '*.cpp' -o -name '*.h' -o -name '*.hpp' -o -name '*.cuh' -o -name 'Makefile' -o -name '*.mk' -o -name 'Instructions*' \) -exec cp -p {} "$OUT/source/" \;
cp -p "$(realpath "$0")" "$OUT/source/run_nvshmem_experiment.sh"
{
  date -u +%FT%TZ
  printf 'Source directory: %s\n' "$PWD"
  printf 'Slurm job: %s\n' "$SLURM_JOB_ID"
  printf 'Nodes: %s\n' "${SLURM_JOB_NODELIST:-unknown}"
  printf 'CUDA_VISIBLE_DEVICES: %s\n' "$CUDA_VISIBLE_DEVICES"
  git rev-parse HEAD 2>/dev/null || true
  git status --short -- . 2>/dev/null || true
  module list 2>&1 || true
  nvcc --version || true
  mpic++ --version || true
  ompi_info --version || true
  nsys --version || true
  scontrol show job "$SLURM_JOB_ID" || true
  # Only relevant tuning variables; avoid dumping tokens/credentials.
  env | grep -E '^(NVSHMEM_|NCCL_|UCX_|OMPI_MCA_|OMP_|CUDA_VISIBLE_DEVICES=|SLURM_CPU_BIND)' | sort || true
} > "$OUT/environment/build_and_job.txt" 2>&1

make -B 2>&1 | tee "$OUT/logs/build.log"
cp -p ./jacobi "$OUT/source/jacobi"
( cd "$OUT/source"; find . -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum ) > "$OUT/source.sha256"
ldd ./jacobi > "$OUT/environment/ldd.txt" 2>&1 || true

# Probe the allocated compute node, not the login node.
srun -N 1 -n 1 bash -c 'hostname; nvidia-smi; nvidia-smi topo -m; lscpu' > "$OUT/environment/compute_node.txt" 2>&1 || true

printf 'kind\trun\tnccheck\tniter\tstart_utc\tend_utc\texit_code\n' > "$OUT/runs.tsv"
# Use the same Slurm flags for every run. Record actual per-rank placement.
LAUNCH=(srun -N 1 --cpu-bind=verbose,sockets --unbuffered -n "$GPUS")
RANK_WRAPPER='printf "[placement] job=%s step=%s rank=%s host=%s CUDA_VISIBLE_DEVICES=%s " "${SLURM_JOB_ID:-?}" "${SLURM_STEP_ID:-?}" "${SLURM_PROCID:-?}" "$(hostname)" "${CUDA_VISIBLE_DEVICES:-unset}"; grep Cpus_allowed_list /proc/self/status; exec "$@"'
run_one() {
  local kind=$1 tag=$2 check=$3 iters=$4; shift 4
  local log="$OUT/logs/$tag.log" start end rc
  local -a cmd=("${LAUNCH[@]}" bash -c "$RANK_WRAPPER" _ "$@")
  start=$(date -u +%FT%TZ)
  { printf '# command: '; printf '%q ' "${cmd[@]}"; printf '\n# start UTC: %s\n' "$start"; } > "$log"
  echo "Running $tag"
  if "${cmd[@]}" 2>&1 | tee -a "$log"; then rc=0; else rc=$?; fi
  end=$(date -u +%FT%TZ)
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$kind" "$tag" "$check" "$iters" "$start" "$end" "$rc" >> "$OUT/runs.tsv"
  printf '# end UTC: %s; exit code: %s\n' "$end" "$rc" >> "$log"
  if (( rc != 0 )); then echo "Run failed ($rc); raw log retained." >&2; fi
}

for ((r=1; r<=REPEATS; r++)); do
  # Reverse order every other repetition to reduce order bias.
  if (( r % 2 )); then checks=(1 10); else checks=(10 1); fi
  for c in "${checks[@]}"; do
    tag=$(printf 'bench_g04_nx16384_ny16384_it%04d_nc%03d_r%02d' "$NITER" "$c" "$r")
    run_one benchmark "$tag" "$c" "$NITER" ./jacobi -nx "$NX" -ny "$NY" -niter "$NITER" -nccheck "$c"
  done
done

# Keep profile results separate from timing statistics.
if [[ "$PROFILE" == 1 ]]; then
  for c in 1 10; do
    tag=$(printf 'trace_g04_nx16384_ny16384_it%04d_nc%03d_r01' "$PROFILE_ITERS" "$c")
    run_one profile "$tag" "$c" "$PROFILE_ITERS" nsys profile --trace=cuda,nvtx,mpi --sample=none --cpuctxsw=none --output="$OUT/profiles/$tag.rank%q{SLURM_PROCID}" ./jacobi -nx "$NX" -ny "$NY" -niter "$PROFILE_ITERS" -nccheck "$c"
  done
fi

# Readable raw summary; exclude profile logs and failed runs.
{
  printf 'Benchmark results (successful srun only; see runs.tsv for failures)\n'
  while IFS=$'\t' read -r kind tag check iters start end rc; do
    [[ "$kind" == benchmark && "$rc" == 0 ]] || continue
    printf '%s: ' "$tag"
    grep 'speedup:' "$OUT/logs/$tag.log" || printf 'NO PERFORMANCE LINE (inspect log)\n'
  done < "$OUT/runs.tsv"
} | tee "$OUT/summary.txt"
printf '\nSaved to: %s\n' "$OUT"
printf 'Add observations to README.md, then archive:\n  tar -czf %q -C %q %q\n' "$OUT.tar.gz" "$ROOT" "$(basename "$OUT")"
