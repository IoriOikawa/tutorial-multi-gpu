# Missing information, experiments, and screenshots

[English](MISSING_INFORMATION.en.md) | [简体中文](MISSING_INFORMATION.md) | [日本語](MISSING_INFORMATION.ja.md)

Record date: 2026-11-15 (America/Chicago). For reviewing and reproducing the experiments after the course. English translation: 2026-11-16.

This checklist is for readers adding evidence later. The original traces are already in the repository. Most tasks below require exporting screenshots from them or recovering missing output, rather than finding files already preserved. Keep the rank, time scale, stream identifiers, kernel names, and NVTX ranges in each screenshot. State the original filename and iteration window in its caption.

## Recover information that affects the conclusions first

- **Chapter 04 numerical checks:** Add rerun logs after extending checks to the last valid row and non-finite values. Preserve the original data. This determines the scope of any claim that numerical validation passed.
- **Chapter 07 NCCL Host output:** Preserve the full command, exit code, grid dimensions, iteration count, `nccheck`, numerical checks, and final time from the formal run. Only source and traces for 4 ranks are currently available; there is no verifiable formal benchmark text.
- **Early NVSHMEM anomaly comparison:** Recover the original log and placement for job 2925255, `nccheck=1`, 0.4770 s. The 2.4381 s log from job 2925303 is already in the repository. The controlled recheck within one job is also preserved; it did not reproduce the old anomaly.
- **Initial NCCL Device failure:** Recover the original terminal output or screenshot showing the mismatch on the first valid row. Corrected successful logs and source are preserved. Only the contemporary description of the initial failure is available.
- **Exact NCCL version:** Add actual `ncclGetVersion` output or shared-library version evidence. `default-CUDA-13` is a module selection, not an exact library version.

## Export these screenshots from existing traces

- **MPI overlap:** Export a stable iteration window from the corrected Chapter 04 `nccheck10` rank 0 trace. Expand interior computation, boundary computation, and MPI calls. Add the same window from another rank to check for asymmetric waiting.
- **NCCL Host:** Export a window showing computation and communication streams from `jacobi.07H-NCCL-task__20261115-2147`. Describe the visible overlap intervals. Leave the overlap percentage unset until it has been measured.
- **NVSHMEM Host:** Export the same time range for all ranks from the early `nvshmem_overlap` traces. Expand barrier, put/quiet, and computation. State that these runs differ from the later 6 controlled benchmarks.
- **NCCL Device LSA:** Export kernel names, device communication ranges, and final synchronization from `nccl-device-lsa-fix`. Check the recorded 3.642 ms host range and 3.627 ms GPU projection range. This review has not independently measured those values.
- **CUDA Graph ON/OFF:** Select matching iteration counts and horizontal-axis ranges from the two trace groups in job 2926183. Expand graph nodes to show dependencies among boundary work, NCCL, interior computation, and norm checks. All eight traces are preserved.
- **Three NVSHMEM Device configurations:** Export the same stable window from scalar, scalar-1d, and block in job 2928756. Keep kernel shapes and barriers visible. Expand other ranks if needed. All twelve traces are preserved.

## Questions that require new measurements

Efficiency with matched single-GPU kernels, statistical stability of Graph priority, and triggers for the Host anomaly require new experiments. Screenshots cannot replace these data. Methods and completion criteria are listed in [open research questions](OPEN_QUESTIONS.en.md).

## Evidence coverage and tool limits

The conversation-reading interface did not return attached images or file contents. Reports use the actual archive and do not infer results from those attachments. Complete launch arguments and executable mappings for earlier Chapter 04 profiles were also not fully preserved. Check the original terminal records to confirm them.

The current review environment has no `nsys`. Binary reports were not opened individually, and GUI screenshots were not exported. Four existing measurement figures use log data directly from [benchmarks.csv](data/benchmarks.csv). Schematic timelines do not replace real profiling evidence.
