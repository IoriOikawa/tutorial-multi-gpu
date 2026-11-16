# SC26 Tutorial: Efficient Distributed GPU Programming for Exascale

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5745504.svg)](https://doi.org/10.5281/zenodo.5745504)


Repository with talks and exercises of our Efficient GPU Programming for Exascale tutorial, to be held at [SC26](https://sc26.conference-program.com/presentation/?id=tut120&sess=sess190).

## Experiment records from 15 November 2026

This fork preserves the completed source snapshots, experiment logs, and reports in English, Simplified Chinese, and Japanese. The three-language documentation was prepared on 16 November 2026. The original tutorial exercises remain in place. Completed implementations and evidence are under each chapter's `reports/2026-11-15/archive/`. The reports distinguish observations, failed runs, and questions that still need validation.

- [Chapter 04: MPI overlap and timing correction](04-H_Overlap_Communication_and_Computation_MPI/reports/2026-11-15/README.en.md)
- [Chapter 07: NCCL Host API](07-H_NCCL_NVSHMEM/reports/2026-11-15/nccl-host.en.md)
- [Chapter 07: NVSHMEM Host and slowdown follow-up](07-H_NCCL_NVSHMEM/reports/2026-11-15/nvshmem-host.en.md)
- [Chapter 09: NCCL Device LSA writes](09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nccl-device.en.md)
- [Chapter 09: CUDA Graph node priority](09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/cuda-graphs.en.md)
- [Chapter 09: Three NVSHMEM Device configurations](09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nvshmem-device.en.md)

Start with the [environment, timing conventions, and evidence index](docs/experiments/2026-11-15/README.en.md). See also [missing information and screenshots](docs/experiments/2026-11-15/MISSING_INFORMATION.en.md) and [open research questions](docs/experiments/2026-11-15/OPEN_QUESTIONS.en.md). The 56 Nsight reports retain their original bytes. The GPU experiments were not rerun during documentation work.

## Coordinates

* Date: 15 November 2026
* Occasion: SC26 Tutorial (Full Day)
* Tutors: Simon Garcia de Gonzalo (SNL), Oded Green (NVIDIA), Andreas Herten (JSC), Lena Oden (Uni Hagen)
* Support: David Appelhans (NVIDIA), Markus Hrywniak (NVIDIA), and Jiri Kraus (NVIDIA)


## Setup

The tutorial is an interactive tutorial with introducing lectures and practical exercises to apply knowledge. The exercises have been derived from the Jacobi solver implementations available in [NVIDIA/multi-gpu-programming-models](https://github.com/NVIDIA/multi-gpu-programming-models).

Overview (only possible on-site at SC26!):

* Sign up at JuDoor
* Open Jupyter JSC: https://jupyter.jsc.fz-juelich.de
* Create new Jupyter instance on [JUPITER, using training26XX account, on **LoginNode**](https://jupyter.jsc.fz-juelich.de/workshops/sc26mg) [^1]
* Source course environment: `source $PROJECT_training26XX/env.sh`
* Sync material: `jsc-material-sync`
* Locally install NVIDIA Nsight Systems: https://developer.nvidia.com/nsight-systems


1. Lecture: Tutorial Overview, Introduction to System + Onboarding *Andreas*
2. Lecture: Introduction to MPI-Distributed Computing with GPUs *Simon*
3. Lecture: Optimization techniques for multi-GPU applications *Simon*
4. Hands-on: Overlap communication and computation with MPI
5. Lecture: Performance / Debugging Tools 
6. Lecture: Overview of NCCL and NVSHMEN in MPI *Lena*
7. Hands-on: Using NCCL and NVSHMEM
8. Lecture: CUDA Graphs and Device-initiated Communication with NCCL and NVSHMEM *Oded*
9. Hands-on: Device-initiated Communication with NVSHMEM and NCCL
10. Lecture: Conclusion and Outline of Advanced Topics *Andreas*

[^1]: JUPITER is the default. In the case the tutors tell to move to the backup (JUWELS Booster), launch a [new Jupyter instance here](https://jupyter.jsc.fz-juelich.de/workshops/sc26mg-juwels).
