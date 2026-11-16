# Technical matters from the day's conversations

[English](CONVERSATION_NOTES.en.md) | [简体中文](CONVERSATION_NOTES.md) | [日本語](CONVERSATION_NOTES.ja.md)

Record date: 2026-11-15 (America/Chicago). For reviewing and reproducing the experiments after the course. English translation: 2026-11-16.

This page preserves experiment-related collaboration matters so readers can distinguish completed work from later plans. Sources are relevant conversations from “Distributed GPU Fundamentals Crash Course” and the supplied experiment archive. Personal exchanges are excluded.

## Completed work supported by files

- **Completed implementation snapshots:** Added communication and dependencies in the MPI, NCCL, NVSHMEM, and CUDA Graph exercises. Code is attached to the chapter reports.
- **Reviewed timing definitions:** Chapter 04 waits for the GPU before the solve ends. Later NVSHMEM Device runs use the maximum rank time. Timing definitions still differ across stages.
- **Corrected LSA writes:** Completed remote stores and team-rank conversion in the NCCL Device course task. Preserved the corrected benchmark and 4-rank traces.
- **Expanded comparison configurations:** Added a scalar configuration with the same 256×1 layout in NVSHMEM Device to distinguish thread-block shape from block communication granularity.
- **Completed the archive:** Verified the input archive checksum and preserved 14 groups of 4-rank traces. Runs with invalid allocations retain their failed status.

Source or logs support these items. This review did not rerun them on the cluster. AI assistance supplied code and analysis suggestions; actual builds, runs, and original output came from the day's experiment environment.

## Proposed work that remains unfinished

First, use matching thread-block shapes for single-GPU and multi-GPU references before explaining efficiency above 100%. Second, add paired repeated measurements of CUDA Graph priority. Third, investigate the early NVSHMEM Host slowdown.

This review adds one status update: the third item already has a controlled recheck, which did not reproduce the early slowdown. Reproducible triggering, synchronization-schedule ablation, and a causal explanation remain unfinished. See [open research questions](OPEN_QUESTIONS.en.md).

## Limits of the conversation evidence

Readable conversations include text summaries and file inventories. The conversation-reading interface did not return attached file or image contents. Reports therefore use archived source and logs as primary evidence. They do not treat chat suggestions as executed commands or add result values unsupported by logs.
