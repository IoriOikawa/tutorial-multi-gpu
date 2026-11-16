# SC26 Tutorial: Efficient Distributed GPU Programming for Exascale

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5745504.svg)](https://doi.org/10.5281/zenodo.5745504)


Repository with talks and exercises of our Efficient GPU Programming for Exascale tutorial, to be held at [SC26](https://sc26.conference-program.com/presentation/?id=tut120&sess=sess190).

## 当天实验记录（2026-11-15）

本 fork 保存了当天完成的代码快照、实验日志和中文报告。原课程练习保留在原位置，完成版本及结果位于各章 `reports/2026-11-15/archive/`。报告区分已有观测、失败记录和待验证问题。

- [第 04 章：MPI 重叠与计时修正](04-H_Overlap_Communication_and_Computation_MPI/reports/2026-11-15/README.md)
- [第 07 章：NCCL Host API](07-H_NCCL_NVSHMEM/reports/2026-11-15/nccl-host.md)
- [第 07 章：NVSHMEM Host 与异常复查](07-H_NCCL_NVSHMEM/reports/2026-11-15/nvshmem-host.md)
- [第 09 章：NCCL Device LSA 写入](09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nccl-device.md)
- [第 09 章：CUDA Graph 节点优先级](09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/cuda-graphs.md)
- [第 09 章：NVSHMEM Device 三种配置](09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nvshmem-device.md)

统一入口：[环境、计时口径与原始资料索引](docs/experiments/2026-11-15/README.md)。另见 [待补信息与截图](docs/experiments/2026-11-15/MISSING_INFORMATION.md)、[后续研究问题](docs/experiments/2026-11-15/OPEN_QUESTIONS.md)。56 份 Nsight 报告按原字节保存；当前整理没有在集群重跑实验。

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
