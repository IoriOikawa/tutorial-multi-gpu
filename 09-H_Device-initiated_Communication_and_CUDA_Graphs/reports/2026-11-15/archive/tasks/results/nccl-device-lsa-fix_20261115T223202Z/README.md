# NCCL Device API - LSA Halo Exchange Fix

## Background
SC26 Hands-On 9C, JUPITER.

The initial implementation failed numerical validation
on the first owned row of all four ranks.

## Root cause identified by source review
The LSA branch of put_to_peer() contained no remote store.
Both host and device use_gin_for_peer() returned false.

## Changes
- Implemented host and device GIN/LSA selection.
- Translated world ranks into LSA team ranks.
- Implemented direct remote stores to symmetric windows.

## Validation
Run the original four-GPU Jacobi benchmark.
Require numerical validation before performance analysis.

## Nsight Systems Observation

Configuration:
- 4 GPUs, 16384 x 16384 mesh
- 10 iterations, nccheck=10
- Rank 0 trace

Measured NVTX durations:
- Single-GPU reference: 17.048 ms
- NCCL Device host solve: 3.642 ms
- NCCL Device GPU-projected solve: 3.627 ms

Observations:
- Fused Jacobi kernels execute on Stream 67.
- Steady-state iteration spacing is approximately
  335 microseconds.
- Host enqueues subsequent iterations and waits
  in the final cudaDeviceSynchronize.
- No millisecond-scale synchronization outlier
  is visible in this trace.
- No standalone halo PtoP memcpy is visible,
  consistent with device-side remote stores.

Limitations:
- Exact synchronization kernel durations and
  template specialization require inspection.
- Intra-kernel communication overlap is not
  quantified by this trace.
- This is a single profiled run, not a controlled
  performance comparison against other solvers.
