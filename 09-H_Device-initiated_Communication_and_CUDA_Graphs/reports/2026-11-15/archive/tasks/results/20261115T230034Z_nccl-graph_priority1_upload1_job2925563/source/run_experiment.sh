#!/usr/bin/env bash
# SC26 Jacobi experiment recorder for a single-node JUPITER allocation.
set -euo pipefail
METHOD=${1:-}
case "$METHOD" in mpi|mpi-overlap|nccl|nccl-overlap|nvshmem|nccl-device|nccl-graph) ;; *) echo 'Usage: run_experiment.sh {mpi|mpi-overlap|nccl|nccl-overlap|nvshmem|nccl-device|nccl-graph}' >&2; exit 2;; esac
[[ -f Makefile && ( -f jacobi.cpp || -f jacobi.cu ) ]] || { echo 'Run from the Jacobi source directory.' >&2; exit 2; }
: "${SLURM_JOB_ID:?Run inside a valid salloc allocation first.}"
GPUS=${GPUS:-4}; NX=${NX:-16384}; NY=${NY:-16384}; NITER=${NITER:-1000}
REPEATS=${REPEATS:-3}; CHECKS=${CHECKS:-'1 10'}; PROFILE=${PROFILE:-0}; PROFILE_ITERS=${PROFILE_ITERS:-10}; PROFILE_CHECKS=${PROFILE_CHECKS:-10}
SMOKE=${SMOKE:-0}; NODE_PRIORITY=${NODE_PRIORITY:-1}; GRAPH_UPLOAD=${GRAPH_UPLOAD:-1}
for v in GPUS NX NY NITER REPEATS PROFILE_ITERS; do [[ ${!v} =~ ^[1-9][0-9]*$ ]] || { echo "Invalid positive integer: $v" >&2; exit 2; }; done
for v in PROFILE SMOKE NODE_PRIORITY GRAPH_UPLOAD; do [[ ${!v} =~ ^[01]$ ]] || { echo "Invalid switch: $v" >&2; exit 2; }; done
read -r -a checks <<< "$CHECKS"; read -r -a profile_checks <<< "$PROFILE_CHECKS"
for c in "${checks[@]}" "${profile_checks[@]}"; do [[ $c =~ ^[1-9][0-9]*$ ]] || exit 2; done
((${#checks[@]} > 0 && ${#profile_checks[@]} > 0)) || exit 2
[[ ${SLURM_JOB_NUM_NODES:-1} == 1 ]] || { echo 'Use a single-node allocation.' >&2; exit 2; }
# Preserve Slurm's GPU visibility for other methods. NVSHMEM tutorial requires all local GPUs visible.
if [[ $METHOD == nvshmem && -z ${CUDA_VISIBLE_DEVICES:-} ]]; then
  CUDA_VISIBLE_DEVICES=$(seq -s, 0 "$((GPUS-1))"); export CUDA_VISIBLE_DEVICES
fi
extra=(); variant=default
if [[ $METHOD == nccl-graph ]]; then
  variant="priority${NODE_PRIORITY}_upload${GRAPH_UPLOAD}"
  [[ $NODE_PRIORITY == 1 ]] || extra+=(-no_node_priority)
  [[ $GRAPH_UPLOAD == 1 ]] || extra+=(-no_graph_upload)
fi
ROOT=$(realpath -m "${RESULT_ROOT:-../results}"); mkdir -p "$ROOT"
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
OUT="$ROOT/${STAMP}_${METHOD}_${variant}_job${SLURM_JOB_ID}"; mkdir "$OUT"
mkdir "$OUT"/{source,environment,logs,profiles}
printf 'Experiment directory: %s\n' "$OUT"
cat > "$OUT/README.md" <<NOTES
# $METHOD / $variant

SC26 multi-GPU Jacobi research, JUPITER.
- Created (UTC): $STAMP
- Allocation: $SLURM_JOB_ID; nodes: ${SLURM_JOB_NODELIST:-unknown}
- Mesh: $NX x $NY; GPUs: $GPUS; max iterations: $NITER
- Norm-check intervals: $CHECKS; repetitions: $REPEATS
- CPU binding: sockets; one allocation; alternating treatment order
- Graph options: $variant (only applicable to nccl-graph)
- Profiling: $PROFILE; iterations: $PROFILE_ITERS; checks: $PROFILE_CHECKS
- Optional correctness smoke tests: $SMOKE

## Research question / pre-run note
${NOTE:-Compare runtime and numerical validation across norm-check intervals under a controlled allocation.}

## Interpretation (fill after execution)
- Numerical validation:
- Performance and variability:
- Unexpected events:
- Limitations and next steps:

Raw timing and profiler runs are separate. See runs.tsv, summary.txt, source/,
environment/, logs/, and profiles/. Runtime is the solver's printed timing,
not initialization or total Slurm elapsed time.
NOTES
find . -maxdepth 1 -type f \( -name '*.cu' -o -name '*.cpp' -o -name '*.h' -o -name '*.hpp' -o -name '*.cuh' -o -name 'Makefile' -o -name '*.mk' -o -name 'Instructions*' \) -exec cp -p {} "$OUT/source/" \;
cp -p "$(realpath "$0")" "$OUT/source/run_experiment.sh"
{
  date -u +%FT%TZ; printf 'Source directory: %s\n' "$PWD"
  git rev-parse HEAD 2>/dev/null || true
  git status --short -- . 2>/dev/null || true
  module list 2>&1 || true
  nvcc --version || true; mpic++ --version || true; nsys --version || true
  scontrol show job "$SLURM_JOB_ID" || true
  env | grep -E '^(NVSHMEM_|NCCL_|UCX_|OMPI_MCA_|OMP_|CUDA_VISIBLE_DEVICES=|SLURM_CPU_BIND)' | sort || true
} > "$OUT/environment/build_and_job.txt" 2>&1
printf 'kind\trun\tnccheck\tniter\tstart_utc\tend_utc\texit_code\tvalidation\n' > "$OUT/runs.tsv"
if ! make -B 2>&1 | tee "$OUT/logs/build.log"; then
  echo 'Build failed; see logs/build.log.' | tee -a "$OUT/README.md" >&2; exit 1
fi
cp -p ./jacobi "$OUT/source/jacobi"
( cd "$OUT/source"; find . -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum ) > "$OUT/source.sha256"
ldd ./jacobi > "$OUT/environment/ldd.txt" 2>&1 || true
srun -N 1 -n 1 bash -c 'hostname; nvidia-smi; nvidia-smi topo -m; lscpu' > "$OUT/environment/compute_node.txt" 2>&1 || true
LAUNCH=(srun -N 1 --cpu-bind=verbose,sockets --unbuffered -n "$GPUS")
WRAPPER='printf "[placement] job=%s step=%s rank=%s host=%s CUDA_VISIBLE_DEVICES=%s " "${SLURM_JOB_ID:-?}" "${SLURM_STEP_ID:-?}" "${SLURM_PROCID:-?}" "$(hostname)" "${CUDA_VISIBLE_DEVICES:-unset}"; grep Cpus_allowed_list /proc/self/status; exec "$@"'
failed=0
run_one() {
  local kind=$1 tag=$2 check=$3 iters=$4; shift 4
  local log="$OUT/logs/$tag.log" start end rc validation
  local -a cmd=("${LAUNCH[@]}" bash -c "$WRAPPER" _ "$@")
  start=$(date -u +%FT%TZ)
  { printf '# command: '; printf '%q ' "${cmd[@]}"; printf '\n# start UTC: %s\n' "$start"; } > "$log"
  echo "Running $tag"
  if "${cmd[@]}" 2>&1 | tee -a "$log"; then rc=0; else rc=$?; fi
  end=$(date -u +%FT%TZ)
  if ((rc != 0)); then validation=FAIL; failed=1
  elif grep -q 'speedup:' "$log"; then validation=PASS
  else validation=UNCONFIRMED; failed=1; fi
  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$kind" "$tag" "$check" "$iters" "$start" "$end" "$rc" "$validation" >> "$OUT/runs.tsv"
  printf '# end UTC: %s; exit code: %s; validation: %s\n' "$end" "$rc" "$validation" >> "$log"
}
if [[ $SMOKE == 1 ]]; then
  # Odd/even iteration count and uneven row partition; no performance comparison.
  for i in 3 4; do
    tag=$(printf 'smoke_g%02d_nx0256_ny0259_it%04d_nc003' "$GPUS" "$i")
    run_one smoke "$tag" 3 "$i" ./jacobi -nx 256 -ny 259 -niter "$i" -nccheck 3 "${extra[@]}"
  done
  if ((failed)); then echo 'Smoke validation failed; benchmark skipped.' | tee -a "$OUT/README.md" >&2; exit 1; fi
fi
for ((r=1;r<=REPEATS;r++)); do
  for ((j=0;j<${#checks[@]};j++)); do
    if ((r%2)); then c=${checks[j]}; else c=${checks[${#checks[@]}-1-j]}; fi
    tag=$(printf 'bench_g%02d_nx%d_ny%d_it%04d_nc%03d_r%02d' "$GPUS" "$NX" "$NY" "$NITER" "$c" "$r")
    run_one benchmark "$tag" "$c" "$NITER" ./jacobi -nx "$NX" -ny "$NY" -niter "$NITER" -nccheck "$c" "${extra[@]}"
  done
done
if [[ $PROFILE == 1 ]]; then
  graph_trace=(); [[ $METHOD != nccl-graph ]] || graph_trace+=(--cuda-graph-trace=node)
  for c in "${profile_checks[@]}"; do
    tag=$(printf 'trace_g%02d_nx%d_ny%d_it%04d_nc%03d_r01' "$GPUS" "$NX" "$NY" "$PROFILE_ITERS" "$c")
    run_one profile "$tag" "$c" "$PROFILE_ITERS" nsys profile --trace=cuda,nvtx,mpi --sample=none --cpuctxsw=none "${graph_trace[@]}" --output="$OUT/profiles/$tag.rank%q{SLURM_PROCID}" ./jacobi -nx "$NX" -ny "$NY" -niter "$PROFILE_ITERS" -nccheck "$c" "${extra[@]}"
  done
fi
{
  printf 'Validated benchmark results only (profile and smoke excluded)\n'
  while IFS=$'\t' read -r kind tag check iters start end rc validation; do
    [[ $kind == benchmark && $validation == PASS ]] || continue
    printf '%s: ' "$tag"; grep 'speedup:' "$OUT/logs/$tag.log"
  done < "$OUT/runs.tsv"
} | tee "$OUT/summary.txt"
printf '\nSaved to: %s\nArchive after updating README:\n  tar -czf %q -C %q %q\n' "$OUT" "$OUT.tar.gz" "$ROOT" "$(basename "$OUT")"
exit "$failed"
