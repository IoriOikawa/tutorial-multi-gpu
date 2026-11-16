# SC26 GPU research checkpoint — 16 November 2026

Review the evidence for MPI numerical validation and the NVSHMEM reference-geometry experiment.

Date: 2026-11-16. Audience: researchers reviewing or reproducing these GPU experiments.

## Overview

The archived logs support 12 successful Chapter04 positive tests and three correctly rejected negative controls. Chapter09A contains 64 primary measurements and nine additional valid repetitions. All 73 accepted measurements passed full-interior numerical validation. These checks were repeated against archived files on a Mac; the GPU experiments were not rerun.

At `nccheck=10`, changing the single-GPU reference geometry reduces median reported efficiency from 105.5985% to 92.8498%, while the four-GPU runtime stays nearly unchanged. This supports reference-geometry mismatch as the explanation for the apparent superlinear efficiency. It does not establish same-implementation strong scaling or prove an atomic-contention mechanism.

Read the [original research log](RESEARCH_LOG.original.md) for the author's complete account. It is preserved byte for byte. Use the [verification record](VERIFICATION.md) for the checks performed during archiving.

## Find the evidence

- [Chapter04 validation results](chapter04-mpi-validation/validation_results.csv): six baseline passes, six overlap passes, and NaN/Inf/finite-error failures.
- [Chapter09A primary dataset](chapter09a-nvshmem/summary/20261116T155724Z/benchmark_results.csv): eight repetitions for each configuration and norm-check interval.
- [All accepted measurements](chapter09a-nvshmem/summary/20261116T155724Z/all_valid_results.csv), [extra repetitions](chapter09a-nvshmem/summary/20261116T155724Z/extra_repeats.csv), and [rejected logs](chapter09a-nvshmem/summary/20261116T155724Z/rejected_logs.csv).
- [Allocation summaries](chapter09a-nvshmem/summary/20261116T155724Z/summary_by_allocation.csv) and [recomputed medians](chapter09a-nvshmem/summary/medians.csv).
- [Evidence mapping](evidence-map.csv): publication paths, original checkpoint paths, and SHA-256 hashes.
- [Provenance](provenance.json): identities of the original ZIP, checkpoint archive, and research log.

Chapter directories retain the relative layout expected by the original scripts. Source snapshots are in `source/` and `work/`; the Chapter04 baseline also has `baseline_strict/original/` and `baseline_strict/work/`. Original patches and per-build hash manifests remain beside those directories.

## Interpret the comparison

The following table is intended for GitHub's desktop document view. NVSHMEM is NVIDIA's shared-memory communication library. Here, a processing element (PE) corresponds to one GPU process. `nccheck` is the norm-check interval in iterations.

| Mode | Single-GPU reference | Four-GPU solver |
|---|---|---|
| A | 32×32 threads/block | Scalar 2D |
| B | 32×32 threads/block | Scalar 1D |
| C | 256×1 threads/block | Scalar 1D |
| D | 256×1 threads/block | Block-cooperative put |

All primary measurements use a 16,384×16,384 grid, 1,000 iterations and four GPUs. Each mode/interval has eight primary measurements. Five Slurm allocations cover four compute nodes. Primary selection favors the original run, then the earliest valid resumed run; it does not select the fastest timing. Nine valid duplicates remain separate.

![Primary median runtimes and reported efficiencies for modes A–D at norm-check intervals 1 and 10. For interval 10, modes B and C have almost identical four-GPU runtimes but efficiencies of 105.60% and 92.85% because their single-GPU references differ.](figures/matched-geometry.png)

Reported efficiency is `100 × ref_sec / (4 × parallel_sec)`. The table and plot use the median of each recorded metric independently; the median efficiency need not equal the ratio of the median runtimes. `parallel_sec` is the maximum rank solver time. The recorded reference also includes `ref_max_sec`, but reported efficiency uses `ref_sec`.

The geometry performance ordering reverses between norm-check intervals 1 and 10. Extra block reductions or global atomics are a hypothesis for future profiling. The Chapter04 baseline and overlap timings came from separate allocations and support a descriptive comparison. An earlier failed baseline smoke attempt remains in the logs, separate from the 12 successful tests.

## Reproduce the analysis

1. From this directory, verify publication bytes with `shasum -a 256 -c SHA256SUMS`.
2. Enter `chapter09a-nvshmem/work` and run `python3 ../summarize_matched.py`. This creates a new UTC-stamped summary directory; the six CSV tables should have the same parsed rows as `../summary/20261116T155724Z/`.
3. From this directory, run `python3 figures/plot_results.py` with Matplotlib installed to regenerate the figure. The plot uses only the 64 primary rows.

To rerun GPU experiments, use a compatible NVIDIA GPU cluster with CUDA, MPI (Message Passing Interface), NVSHMEM and the course environment. The preserved Makefiles use environment-specific compiler and library paths. Rebuild in a working copy. The old `build.sha256` files describe the archived binaries and sources; binaries are intentionally absent here, and a new build may have a different hash.

After securing a suitable four-GPU Slurm allocation, the original Chapter09A `resume_matched.py --run` can run missing cases. With the complete preserved logs present it finds no missing cases. To collect a new experiment, use a separate working copy and a fresh log directory; retain this evidence unchanged. No cluster reservation or allocation is requested by the analysis commands above.

## Understand the publication boundary

The full original ZIP and checkpoint archive remain local. This directory excludes compiled executables, object files, Python caches, macOS metadata, build logs, allocation dumps and GPU inventories. Selected evidence files and the original research log are unchanged. There was no need to rewrite their content: personal account information occurs in excluded metadata.

Slurm job identifiers and compute-node labels remain in CSVs and run logs because they support allocation pairing. The [release review](RELEASE_REVIEW.md) records this disclosure and the exact exclusions. The [third-party notices](THIRD_PARTY_NOTICES.md) identify the source-file licenses. The checkpoint contains only the two November 16 research directories; it does not include the previous day's 56 Nsight Systems reports.
