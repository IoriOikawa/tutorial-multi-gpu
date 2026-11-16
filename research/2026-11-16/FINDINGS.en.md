# Findings and progress against earlier questions

[English](FINDINGS.en.md) | [简体中文](FINDINGS.md) | [日本語](FINDINGS.ja.md)

Compare the November 16 evidence with the main branch's November 15 questions and missing-information checklist.

Date: 2026-11-16. Audience: researchers deciding which conclusions and follow-up tasks the evidence supports.

## Overview

The last-row/non-finite validation defects and the reference-geometry explanation now have direct evidence. The original questions are broader, so Q1 and Q4 remain partial; Q2 and Q3 remain open. The corrected Chapter04 rerun-output gap is filled for the tested cases. Other missing historical output, exact NCCL runtime version and all six screenshot tasks remain open. [Research index](README.en.md) provides the original log, data and reproduction commands.

The comparison baseline is commit `9cccb76`; the preserved research checkpoint is commit `e1985a0`. Status IDs below follow the original section/bullet order. [Structured status](analysis/question_status.json) records that mapping. Tables target GitHub's desktop document view.

## Chapter04 closes the validator defects within the tested scope

The [overlap validator](chapter04-mpi-validation/work/jacobi.cpp#L595) and [baseline validator](chapter04-mpi-validation/baseline_strict/work/jacobi.cpp#L333) include each rank's last owned row, reject non-finite reference or computed values, and reduce coverage/error counts across ranks. [NaN](chapter04-mpi-validation/negative_control/nan.log), [Inf](chapter04-mpi-validation/negative_control/inf.log) and [finite-error](chapter04-mpi-validation/negative_control/finite.log) injections at the last owned row are rejected with process exit code 1.

The [validation table](chapter04-mpi-validation/validation_results.csv) contains six baseline and six overlap passes. Cases cover uneven partitioning (`nx=261`, `ny=259`, four ranks), 3/4 iterations, and sparse checks, including 10 iterations with `nccheck=20`. The large cases check all 268,369,924 interior points with zero maximum absolute error.

Single-row subdomains are not covered: the small-grid cases have 64 or 65 owned rows per rank. The failed preliminary baseline smoke log remains distinct from the 12 passing tests. For the large 1,000-iteration runs, baseline/overlap times are 0.4832/0.4085 s at interval 1 and 0.3998/0.3130 s at interval 10. These are separate-job/node observations, not a controlled repeated speedup comparison.

## Chapter09A explains apparent superlinear efficiency within these settings

NVSHMEM is NVIDIA's shared-memory communication library; here a processing element (PE) is one GPU process. `nccheck` is the periodic norm-check interval. All accepted distributed benchmarks use four PEs, a 16,384×16,384 grid and 1,000 iterations. There are 64 primary measurements (eight per mode/interval), nine extras, eight separate smoke tests and three rejected benchmark logs, across five allocations and four nodes. Allocation coverage is uneven; eight measurements do not mean eight independent allocations. [Allocation summaries](chapter09a-nvshmem/summary/20261116T155724Z/summary_by_allocation.csv) preserve this distinction.

| Mode | Pure-CUDA reference | Four-PE solver |
|---|---|---|
| A | 32×32 | Scalar 2D |
| B | 32×32 | Scalar 1D |
| C | 256×1 | Scalar 1D |
| D | 256×1 | Block-cooperative put |

The reference geometry is selectable in the [matched-geometry patch](chapter09a-nvshmem/matched_geometry.patch). All 73 accepted measurements pass strict full-interior validation with 1,000 reference and distributed iterations. Selection favors the original run, otherwise the earliest valid resumed run; it does not choose the fastest sample.

| nccheck | Mode | Reference median / s | Four-PE median / s | Efficiency median / % |
|---|---|---:|---:|---:|
| 1 | A | 1.680691 | 0.485778 | 86.4564 |
| 1 | B | 1.678612 | 0.595553 | 70.4821 |
| 1 | C | 2.156206 | 0.596066 | 90.9742 |
| 1 | D | 2.153060 | 0.596093 | 90.2988 |
| 10 | A | 1.235957 | 0.330905 | 93.4309 |
| 10 | B | 1.236389 | 0.292782 | 105.5985 |
| 10 | C | 1.088770 | 0.292753 | 92.8498 |
| 10 | D | 1.089082 | 0.297566 | 91.5239 |

Reported efficiency is `100 × ref_sec / (4 × parallel_sec)`; parallel time is the maximum rank time. The recorded `ref_max_sec` is not used in that efficiency. Each column is a separate median, so median efficiency need not equal the ratio of median times.

At interval 10, B→C changes the reference median by −11.940%, while the distributed median changes by −0.010%. Efficiency falls from 105.5985% to 92.8498%. Eight B/C pairs matched by repetition, job and node give median reference change −11.939% and distributed change +0.004%. These comparisons support the reference-geometry explanation for apparent superlinear efficiency. A pure-CUDA reference is still not a same-implementation NVSHMEM 1-PE baseline.

At interval 1, the 256×1 reference is 28.452% slower than 32×32: the ordering reverses. Extra reduction/atomic overhead is a hypothesis requiring separate profiling of norm-enabled and norm-disabled kernels. D has about 1.64% higher median distributed time than C at interval 10; this descriptive difference does not establish a general block-put advantage or statistical significance.

The [summary with quartiles](analysis/primary_summary.csv) uses `statistics.quantiles(n=4, method='inclusive')` on primary samples only. For interval 10, B's distributed Q1/Q3 are 0.292439/0.293538 s; C's are 0.292719/0.293231 s. These pooled descriptive intervals and the [paired medians](analysis/paired_geometry.csv) are not confidence intervals, independent-allocation replication or causal-mechanism proof.

## Compare every original research question

| ID | Original task | Status on 2026-11-16 | Remaining work |
|---|---|---|---|
| Q1 | Matched reference and scaling | Partial: geometry subquestion answered; repeated results preserved | Same-implementation 1 PE/4 PE; complete baseline-equivalence controls and uncertainty |
| Q2 | Stable Graph-priority benefit | Open: no new ON/OFF dataset | Controlled repeated priority comparisons |
| Q3 | Early NVSHMEM Host slowdown | Open: Device measurements do not test Host anomaly | Trigger, placement/environment and controlled reproduction |
| Q4 | Complete Chapter04 checks | Partial: last-row/non-finite fixes and 12/3 tests verified | Single-row subdomains; same-allocation repeated performance comparison |

The [updated questions](../../docs/experiments/2026-11-15/OPEN_QUESTIONS.en.md) preserve the remaining completion criteria. The tested defects are resolved in archived research snapshots; original course `tasks/` and `solutions/` are not replaced by these snapshots.

## Compare the missing-information checklist and keep the next steps visible

| IDs | Missing material | Status |
|---|---|---|
| M1 | Chapter04 corrected-validation rerun logs | Supplied for the logged cases; single-row coverage remains Q4 |
| M2 | Formal NCCL Host output | Open |
| M3 | Old Host job 2925255 log and placement | Open |
| M4 | Original NCCL Device first-failure output | Open |
| M5 | Exact NCCL runtime version used in those experiments | Open; a CI image version cannot recover historical runtime evidence |
| T1–T6 | MPI, NCCL Host, NVSHMEM Host, NCCL Device LSA, Graph, NVSHMEM Device screenshots | All open; new performance bars do not replace trace screenshots |

Unreturned older attachments and earlier Chapter04 profile command/executable mappings remain historical gaps. See the [updated missing-information checklist](../../docs/experiments/2026-11-15/MISSING_INFORMATION.en.md). Next measurements should first fill single-row coverage and same-implementation scaling, then isolate norm/reduction costs. No new GPU execution or profiler screenshots were produced during integration. Original evidence, failed logs and original research prose remain intact.
