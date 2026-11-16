# Open research questions

[English](OPEN_QUESTIONS.en.md) | [简体中文](OPEN_QUESTIONS.md) | [日本語](OPEN_QUESTIONS.ja.md)

Record date: 2026-11-15 (America/Chicago). For reviewing and reproducing the experiments after the course. English translation: 2026-11-16.

This page preserves unfinished experiment questions so that proposals are not presented as results. Related earlier observations remain in the reports and logs linked from the [day's experiment index](README.en.md).

## Recalculate efficiency with matched thread-block configurations

**Current evidence:** The NVSHMEM Device single-GPU reference is fixed at 32×32, while scalar one-dimensional and block modes use 256×1. The observed 0.292928 s and 105.64% do not establish strong scaling with matching kernel shapes.

**Next step:** Match the single-GPU thread block, reduction method, dimensions, iterations, warm-up, and norm checks. Also compare 1 PE and 4 PE using the same NVSHMEM implementation. Distinguish the pure CUDA reference from a 1 PE baseline that includes the communication runtime.

**Completion criteria:** Preserve source and full commands for each configuration. Repeat measurements within one job and report variation. Recalculate speedup and efficiency with matched timings. These new results are not currently available.

## Test whether CUDA Graph node priority gives a stable benefit

**Current evidence:** Each check interval has only one ON/OFF comparison. The single interval-10 observation shows about 4.32% less time. Interval 1 shows no benefit in the same direction.

**Next step:** Fix graph upload, hardware, binding, source, and timing scope. Alternate `ON,OFF,OFF,ON`, for example over 5 rounds, to obtain 10 observations for each treatment. Record the two `nccheck` settings separately.

**Completion criteria:** Preserve individual measurements and report the median, interquartile range, paired differences, and uncertainty. Discuss a stable benefit only if the difference exceeds normal variation and can be reproduced. Timelines help check the mechanism; they do not replace repeated measurements.

## Explain the early NVSHMEM Host slowdown

**Current evidence:** The old 2.4381 s log exists. Later `nccheck=10` results within one job were around 0.3281 s, and the old anomaly did not recur. The source already synchronizes the GPU before stopping the timer.

**Next step:** Record all-rank times, CPU/GPU placement, and environment before trying a controlled reproduction. If it recurs, keep norm frequency fixed. Change only whether the host synchronizes at the end of iterations without norm checks, as an ablation experiment.

**Completion criteria:** Provide reproducible triggers and comparisons, or state clearly that this round still could not reproduce the anomaly. Even if the synchronization ablation changes time, it establishes only that change's effect. It cannot directly identify an internal NVSHMEM root cause.

## Complete Chapter 04 numerical checks

**Current evidence:** The check loop uses a strict less-than comparison against the last valid row index, excluding each rank's last row. It also does not explicitly reject non-finite values. Current logs cannot establish that these cases were validated.

**Next step:** Extend checks in a new implementation version. Rerun with grids that do not divide evenly, single-row subdomains, odd and even iteration counts, and sparse norm checks. Preserve old results and number new results separately.

**Completion criteria:** Print the valid grid range covered and all failure conditions. Preserve rerun logs, then update the Chapter 04 report. This was not implemented during the current archive review.
