# Open research questions

[English](OPEN_QUESTIONS.en.md) | [简体中文](OPEN_QUESTIONS.md) | [日本語](OPEN_QUESTIONS.ja.md)

Record date: 2026-11-15 (America/Chicago). For reviewing and reproducing the experiments after the course. English translation: 2026-11-16.

This page preserves unfinished experiment questions so that proposals are not presented as results. Related earlier observations remain in the reports and logs linked from the [day's experiment index](README.en.md).

## Status update — 2026-11-16

[Today's findings and evidence comparison](../../../research/2026-11-16/FINDINGS.en.md) verifies two core subquestions: Chapter04's last-row/non-finite defects and the NVSHMEM reference-geometry explanation. Q1 and Q4 remain partial because same-implementation 1 PE/4 PE scaling and single-row subdomains are untested. Q2/Q3 have no new results. IDs follow the original section order; older observations remain historical evidence, not newly rerun measurements.

## Recalculate efficiency with matched thread-block configurations

**Status — partial (Q1), 2026-11-16.** The earlier 0.292928 s / 105.64% observation used a 32×32 pure-CUDA reference for a 256×1 distributed solver. The new [64 primary measurements](../../../research/2026-11-16/chapter09a-nvshmem/summary/20261116T155724Z/benchmark_results.csv) and nine extras test selectable reference geometry with strict validation.

**Resolved subquestion:** At `nccheck=10`, B→C changes reference median 1.236389→1.088770 s, parallel median 0.292782→0.292753 s, and reported efficiency 105.5985%→92.8498%. Eight same-job/node/repetition B/C pairs per interval support the reference-geometry explanation. See [statistics and limitations](../../../research/2026-11-16/FINDINGS.en.md).

**Remaining work:** Compare 1 PE and 4 PE using the same NVSHMEM implementation. Distinguish pure CUDA from a baseline including the communication runtime. Complete baseline-equivalence controls for reduction method, dimensions, iterations, warm-up and norm checks; report uncertainty. Eight samples per setting span shared allocations and are not eight independent allocations.

**Completion criteria:** Preserve source and full launch procedures, repeated timings and variation, then calculate same-implementation scaling with documented controls. The geometry subquestion is answered; the broader strong-scaling question stays open.

## Test whether CUDA Graph node priority gives a stable benefit

**Current evidence:** Each check interval has only one ON/OFF comparison. The single interval-10 observation shows about 4.32% less time. Interval 1 shows no benefit in the same direction.

**Next step:** Fix graph upload, hardware, binding, source, and timing scope. Alternate `ON,OFF,OFF,ON`, for example over 5 rounds, to obtain 10 observations for each treatment. Record the two `nccheck` settings separately.

**Completion criteria:** Preserve individual measurements and report the median, interquartile range, paired differences, and uncertainty. Discuss a stable benefit only if the difference exceeds normal variation and can be reproduced. Timelines help check the mechanism; they do not replace repeated measurements.

## Explain the early NVSHMEM Host slowdown

**Current evidence:** The old 2.4381 s log exists. Later `nccheck=10` results within one job were around 0.3281 s, and the old anomaly did not recur. The source already synchronizes the GPU before stopping the timer.

**Next step:** Record all-rank times, CPU/GPU placement, and environment before trying a controlled reproduction. If it recurs, keep norm frequency fixed. Change only whether the host synchronizes at the end of iterations without norm checks, as an ablation experiment.

**Completion criteria:** Provide reproducible triggers and comparisons, or state clearly that this round still could not reproduce the anomaly. Even if the synchronization ablation changes time, it establishes only that change's effect. It cannot directly identify an internal NVSHMEM root cause.

## Complete Chapter 04 numerical checks

**Status — partial (Q4), 2026-11-16.** The old snapshots omit each rank's last row and do not explicitly reject non-finite values. New [overlap](../../../research/2026-11-16/chapter04-mpi-validation/work/jacobi.cpp#L595) and [baseline](../../../research/2026-11-16/chapter04-mpi-validation/baseline_strict/work/jacobi.cpp#L333) snapshots fix both defects and report global coverage/error counts.

**Verified results:** [Twelve positive tests and three negative controls](../../../research/2026-11-16/chapter04-mpi-validation/validation_results.csv) cover uneven grids, odd/even iterations and sparse norm checks. NaN, Inf and finite errors injected at the last owned row fail with exit code 1. Original files and failed preliminary runs are retained.

**Remaining work:** Single-row subdomains have no rerun log; the smallest cases have 64–65 owned rows per rank. Baseline/overlap performance measurements are from separate jobs/nodes and need controlled repeated measurements within one allocation.

**Completion criteria:** Add explicit single-row subdomain tests and preserve their coverage/failure output. Keep the old evidence and new snapshots separately identified. The tested validator defects are resolved; the full requested validation matrix remains incomplete. The [Chapter04 report](../../../04-H_Overlap_Communication_and_Computation_MPI/reports/2026-11-15/README.en.md) links this follow-up.
