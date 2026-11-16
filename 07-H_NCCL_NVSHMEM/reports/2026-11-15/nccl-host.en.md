# Chapter 07: Exchange boundaries with the NCCL Host API

[English](nccl-host.en.md) | [简体中文](nccl-host.md) | [日本語](nccl-host.ja.md)

Record date: 2026-11-15 (America/Chicago). For reviewing and reproducing the experiments after the course. English translation: 2026-11-16.

[Return to the day's experiment index](../../../docs/experiments/2026-11-15/README.en.md) · [Read the missing information and screenshot checklist](../../../docs/experiments/2026-11-15/MISSING_INFORMATION.en.md)

## What the evidence currently supports

The day's source completes NCCL communicator initialization, grouped sends and receives, and dependencies between computation and communication streams. Nsight reports for 4 ranks are preserved. A separately saved formal benchmark text log for this stage is missing. This report therefore records implementation and available evidence without adding unverifiable timings or speedups.

NCCL means NVIDIA Collective Communications Library. This implementation uses host-initiated point-to-point sends and receives. The GPU performs the communication work.

## Implementation completed that day

- **Communicator initialization:** MPI distributes the NCCL identifier, then each rank creates its communicator. See the [initialization source](archive/tasks/NCCL/jacobi.cpp#L206).
- **Boundary exchange:** Two sends and two receives are scheduled between `ncclGroupStart` and `ncclGroupEnd`. See the [exchange within the iteration](archive/tasks/NCCL/jacobi.cpp#L381).
- **Check coverage:** The numerical-comparison loop in this snapshot includes each rank's last row. See the [numerical comparison](archive/tasks/NCCL/jacobi.cpp#L421). This establishes the implemented scope of checks; it cannot replace missing run output.

## Preserved evidence

The [source, Makefile, and exercise instructions](archive/tasks/NCCL/) and 4 `.nsys-rep` files named `jacobi.07H-NCCL-task__20261115-2147` are preserved. Ranks are 0, 1, 2, and 3. The shared [profiles.csv](../../../docs/experiments/2026-11-15/data/profiles.csv) contains the file inventory and SHA-256 hashes.

This review did not open these Nsight files locally or rerun GPU programs. File presence and complete rank coverage establish archive completeness. They do not establish independent verification of every timeline feature or numerical result.

## How to recheck and fill the gaps

With the course environment and a valid GPU allocation, enter the source directory and build with the adjacent Makefile. Preserve the full command, exit code, numerical checks, and solve time. Example arguments are `srun --cpu-bind=sockets -n 4 ./jacobi -nx 16384 -ny 16384 -niter 1000 -nccheck 1`. This is a reproduction suggestion, not a recovery of the missing original command.

Prioritize the original terminal log and timeline screenshots showing boundary kernels, interior kernels, NCCL communication, and stream identifiers. This stage is not currently suitable for a speed ranking across communication libraries.
