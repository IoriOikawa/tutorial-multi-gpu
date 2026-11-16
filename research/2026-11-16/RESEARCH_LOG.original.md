# Research Log — November 16, 2026

## SC26: Efficient Distributed GPU Programming for Exascale

**Platform:** JUPITER Booster, NVIDIA GH200  
**Workload:** Distributed 2D Jacobi relaxation  
**Topics:** MPI, NVSHMEM, numerical correctness, GPU kernel geometry, performance reproducibility

## 1. Research Objectives

Today's work focused on two questions:

1. Can the correctness of the communication-overlapped MPI Jacobi solver be established through comprehensive numerical validation?
2. Why does the NVSHMEM device-initiated Jacobi implementation report an apparent superlinear parallel efficiency of approximately 105.64%?

## 2. Chapter 04 — MPI Communication and Computation Overlap

### Numerical Validation

The original validation logic was strengthened to check every owned interior element, including the last valid row of each MPI rank.

The updated validator:

- Checks both reference and distributed results for non-finite values.
- Computes the maximum absolute numerical error.
- Counts checked elements, non-finite values, and mismatches across all MPI ranks.
- Verifies complete coverage of the interior grid.
- Returns a nonzero exit status when validation fails.

Final GPU synchronization was also added where necessary to ensure that timed solver execution had completed before recording the stopping time.

### Results

- Six positive validation tests for the MPI baseline.
- Six positive validation tests for the communication-overlapped implementation.
- Three negative controls injecting NaN, positive infinity, and a finite numerical error.

All 12 positive tests passed, and all three negative controls were successfully detected.

The largest validation case covered 268,369,924 interior elements, with a maximum absolute error of zero.

### Performance

For a 16,384 × 16,384 grid and 1,000 iterations:

| Configuration | Baseline 4-GPU | Overlap 4-GPU |
|---|---:|---:|
| nccheck=1 | 0.4832 s | 0.4085 s |
| nccheck=10 | 0.3998 s | 0.3130 s |

These measurements were collected in separate allocations. The observed performance improvement is therefore descriptive rather than a fully controlled causal comparison.

## 3. Chapter 09A — NVSHMEM Device-Initiated Communication

### Motivation

An earlier Scalar 1D experiment reported 105.64% parallel efficiency on four GH200 GPUs.

We hypothesized that the apparent superlinear efficiency was influenced by a mismatch between the thread-block geometry of the single-GPU reference and that of the distributed solver.

### Experimental Design

Four configurations were evaluated:

| Mode | Single-GPU Reference | Four-GPU Solver |
|---|---|---|
| A | 32×32 | Scalar 2D |
| B | 32×32 | Scalar 1D |
| C | 256×1 | Scalar 1D |
| D | 256×1 | Block-cooperative Put |

All benchmarks used a 16,384 × 16,384 grid, 1,000 iterations, and four GPUs.

Two norm-check intervals were tested: 1 and 10 iterations.

Eight repetitions were planned for every configuration and norm-check interval, giving 64 primary benchmark measurements.

### Experimental Results

The experiment produced:

- 64 of 64 planned benchmark measurements.
- Nine additional valid repetitions.
- Five Slurm allocations across four compute nodes.
- Eight successful preliminary smoke tests.
- Three rejected or incomplete benchmark logs, excluded from the accepted dataset.

All 73 accepted benchmark measurements passed strict numerical validation across the entire interior grid.

### Final Median Performance

| nccheck | Mode | Reference (s) | Four-GPU (s) | Efficiency |
|---|---|---:|---:|---:|
| 1 | A | 1.680691 | 0.485778 | 86.4564% |
| 1 | B | 1.678612 | 0.595553 | 70.4821% |
| 1 | C | 2.156206 | 0.596066 | 90.9742% |
| 1 | D | 2.153060 | 0.596093 | 90.2988% |
| 10 | A | 1.235957 | 0.330905 | 93.4309% |
| 10 | B | 1.236389 | 0.292782 | 105.5985% |
| 10 | C | 1.088770 | 0.292753 | 92.8498% |
| 10 | D | 1.089082 | 0.297566 | 91.5239% |

### Finding 1 — Reference Geometry Explains Apparent Superlinear Efficiency

At nccheck=10, changing the single-GPU reference from 32×32 to 256×1 reduced median reference runtime by 11.940%.

The distributed solver remained essentially unchanged:

- Median distributed runtime change: −0.010%.
- Same-allocation paired median change: +0.004%.

The reported median efficiency decreased from 105.5985% to 92.8498%.

This provides evidence that reference-kernel geometry mismatch was the primary explanation for the observed superlinear efficiency.

### Finding 2 — Geometry and Norm-Reduction Frequency Interact

The relative performance of the two reference geometries reversed as the norm-check interval changed.

- At nccheck=1, the 256×1 reference was 28.452% slower.
- At nccheck=10, the 256×1 reference was 11.940% faster.

A possible explanation is that the larger number of thread blocks in the 256×1 geometry increases block-reduction and global atomic-add overhead during norm calculation. This mechanism remains a hypothesis requiring further profiling.

### Finding 3 — Block Put Does Not Automatically Improve Performance

The matched-geometry Scalar 1D and Block Put implementations had nearly identical median runtimes at nccheck=1.

At nccheck=10, the Block Put implementation had approximately 1.64% higher median runtime.

No clear performance advantage for block-cooperative puts was demonstrated under the tested single-node workload.

## 4. Reproducibility and Experiment Infrastructure

Several improvements were made to the benchmark workflow:

- SHA-256 verification of source code, Makefiles, and executables.
- Separate log directories for individual Slurm allocations.
- Automatic discovery of benchmark logs.
- Completion markers for successfully validated runs.
- Time-budget-aware checkpoint and resume functionality.
- Automatic exclusion of incomplete and invalid logs.
- Deterministic separation of primary measurements and additional repetitions.
- Per-allocation and paired performance summaries.

An initial resume-script error caused nine repeated benchmark measurements because the original smoke-test directory was mistakenly used as the primary benchmark directory. The issue was corrected without discarding valid results.

## 5. Limitations and Future Work

- Profile norm-enabled and norm-disabled kernels separately.
- Quantify the contributions of atomic contention, occupancy, and memory access behavior using Nsight Compute.
- Conduct same-implementation 1-PE versus 4-PE strong-scaling measurements.
- Investigate the previously observed NVSHMEM host-side performance anomaly.
- Complete controlled repeated measurements of CUDA Graph node priority.
- Extend communication experiments beyond a single compute node.

## 6. Conclusion

Today's experiments demonstrate why numerical correctness, matched reference implementations, and reproducible benchmarking must be established before interpreting distributed GPU performance.

The apparent 105.64% efficiency was transformed from an unexplained observation into a controlled experimental finding. A second, potentially important interaction between kernel geometry and norm-reduction frequency was identified for future investigation.

The complete raw experimental evidence is retained separately in a timestamped, SHA-256-verified research archive.
