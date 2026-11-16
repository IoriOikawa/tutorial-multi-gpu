# nccl-graph / priority0_upload1

SC26 multi-GPU Jacobi research, JUPITER.
- Created (UTC): 20261115T231410Z
- Allocation: 2926183; nodes: jpbo-001-09
- Mesh: 16384 x 16384; GPUs: 4; max iterations: 1000
- Norm-check intervals: 1 10; repetitions: 1
- CPU binding: sockets; one allocation; alternating treatment order
- Graph options: priority0_upload1 (only applicable to nccl-graph)
- Profiling: 1; iterations: 10; checks: 10
- Optional correctness smoke tests: 0

## Research question / pre-run note
Compare runtime and numerical validation across norm-check intervals under a controlled allocation.

## Interpretation (fill after execution)
- Numerical validation:
- Performance and variability:
- Unexpected events:
- Limitations and next steps:

Raw timing and profiler runs are separate. See runs.tsv, summary.txt, source/,
environment/, logs/, and profiles/. Runtime is the solver's printed timing,
not initialization or total Slurm elapsed time.
