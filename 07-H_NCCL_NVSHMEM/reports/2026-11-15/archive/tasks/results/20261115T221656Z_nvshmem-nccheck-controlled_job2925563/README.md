# nvshmem-nccheck-controlled

- Created (UTC): 20261115T221656Z
- Slurm allocation: 2925563
- Nodes: jpbo-003-46
- Method: NVSHMEM host-initiated Jacobi, overlap with quiet/event/barrier
- Mesh: 16384 x 16384; ranks/GPUs: 4; max iterations: 1000
- Treatment: nccheck=1 vs 10; repetitions per treatment: 3
- CPU binding: sockets; one allocation, same executable, alternating order
- Profiling: 0 (separate runs; 100 iterations if enabled)

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
