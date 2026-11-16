# 2026-11-15 SC26 multi-GPU experiment records

[English](README.en.md) | [简体中文](README.md) | [日本語](README.ja.md)

Record date: 2026-11-15 (America/Chicago). For reviewing and reproducing the experiments after the course. English translation: 2026-11-16.

These records help course participants find the day's implementations, results, and questions that still need verification. The experiments follow this repository's distributed GPU tutorial. Start with the [root README](../../../README.md) for the course.

## Findings from the day

The archive preserves implementation snapshots, six reports available in three languages, 22 readable formal or historical benchmark results, and 56 Nsight Systems reports. The original course `tasks/` and `solutions/` files remain unchanged. Completed versions are in each chapter report's `archive/` directory.

- **Preserved implementations:** MPI overlap, NCCL Host, NVSHMEM Host, NCCL Device LSA writes, CUDA Graph, and NVSHMEM Device configurations.
- **Checked follow-up results:** The controlled NVSHMEM Host recheck did not reproduce the early slowdown. CUDA Graph priority has only one comparison per setting. Printed efficiencies above 100% involve different reference kernel configurations.
- **Still needed:** Chapter 04 reruns with last-row and non-finite-value checks, original NCCL Host benchmark output, Nsight screenshots at matching scales, fair baselines, and repeated measurements.

This review checked existing files, source code, and arithmetic only. It did not rebuild or run programs on the GPU cluster. Failed runs are recorded separately from successful runs. Short trace timings are not treated as 1000-iteration benchmarks.

## Read the experiment reports

- **Experiment report:** [Chapter 04: MPI overlap and timing correction](../../../04-H_Overlap_Communication_and_Computation_MPI/reports/2026-11-15/README.en.md)
- **Experiment report:** [Chapter 07: NCCL Host API](../../../07-H_NCCL_NVSHMEM/reports/2026-11-15/nccl-host.en.md)
- **Experiment report:** [Chapter 07: NVSHMEM Host and anomaly recheck](../../../07-H_NCCL_NVSHMEM/reports/2026-11-15/nvshmem-host.en.md)
- **Experiment report:** [Chapter 09: NCCL Device LSA writes](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nccl-device.en.md)
- **Experiment report:** [Chapter 09: CUDA Graph node priority](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/cuda-graphs.en.md)
- **Experiment report:** [Chapter 09: Three NVSHMEM Device configurations](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nvshmem-device.en.md)

Continue with the [missing information and screenshot checklist](MISSING_INFORMATION.en.md), [open research questions](OPEN_QUESTIONS.en.md), and [technical matters from the day's conversations](CONVERSATION_NOTES.en.md).

## Check the environment and timing definitions

The later controlled experiments recorded JUPITER, the course platform, with Slurm partition `booster`, NVIDIA GH200 120GB GPUs, and 4 GPUs on one node. The build environment recorded CUDA 13.3.33, GCC 15.2.0, Open MPI 5.0.10, NVSHMEM 3.8.0, and Nsight Systems 2026.6.1. The NCCL module was named `default-CUDA-13`. Its exact runtime version is unconfirmed; the module name is not treated as a version number.

`nccheck` controls periodic norm checks. Non-CSV mode may also check the norm every 100 iterations for printed output. The printed efficiency for 1 GPU and 4 GPUs is `T1 / (4 × T4) × 100%`. Chapters 04 and 07, NCCL Device, and Graph report rank 0 time. The later NVSHMEM Device implementation reports the maximum time across ranks. These tables therefore do not rank communication libraries under a common timing definition.

Original filenames and log times remain unchanged. `20261116T03...Z` is UTC, which is still 2026-11-15 in Chicago. Cluster terminal times without a stated timezone are not relabeled.

## Trace the original materials

The input was `SC26-Multi-GPU-Tutorial_COMPLETE_20261116T041055Z.tar.gz`, with SHA-256:

```text
2f6feec5cd6d83c84b7d238bc67f589f49ee284802c10347faaa5b58e577ed8b
```

[data/provenance.json](data/provenance.json) maps preserved files to members of the original archive and records their original byte counts and SHA-256 hashes. The 234 original files, about 48 MB, are preserved byte for byte, including 56 binary traces. Executables, object files, nested archives, notebooks without output, and slides and reference solutions already in the repository were not committed again.

- **Measurement table:** [benchmarks.csv](data/benchmarks.csv) links each row to a source log and distinguishes early anomalies, controlled measurements, and timing definitions.
- **Run registry:** [runs.csv](data/runs.csv) merges 33 original registry records, including 6 steps that failed because their allocation expired. No status is invented for older experiments without a registry.
- **Trace inventory:** [profiles.csv](data/profiles.csv) lists 14 groups and 56 files. Each group contains ranks 0, 1, 2, and 3. Completeness describes archive coverage; it does not mean this review opened and verified every binary file.

## Check and reproduce the work

Each report links to the day's source, Makefile, scripts, and logs. Check allocations, modules, and paths in the cluster scripts against your environment before using them. Existing executables are not included; rebuild from the preserved source to reproduce the work.

The directory also preserves the original archive's contents, experiment, and profile inventories. The original `source.sha256` may list executables that were not committed. Use the paths and hashes in `provenance.json` to check current attachments. See also the [same-day CPU tutorial archive](RELATED_RESOURCES.en.md). The full conversations were not copied publicly, and non-experiment content is excluded. The writing follows ISO 24495 plain-language principles. This describes a writing method, not standards certification or proof of experimental correctness.

[plot_results.py](data/plot_results.py) reads the CSV to generate four data figures. The plotting environment used Matplotlib 3.11.2. With Python and Matplotlib installed, run this command from the repository root:

```sh
python3 docs/experiments/2026-11-15/data/plot_results.py
```

See the [translation check record](data/translation-checks.json) for document coverage and consistency checks.
