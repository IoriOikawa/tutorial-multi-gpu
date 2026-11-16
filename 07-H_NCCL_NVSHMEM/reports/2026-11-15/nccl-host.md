# 第 07 章：使用 NCCL Host API 交换边界

记录日期：2026-11-15（America/Chicago）。供课后复习与复现实验使用。

[返回当天实验索引](../../../docs/experiments/2026-11-15/README.md) · [查看待补信息与截图清单](../../../docs/experiments/2026-11-15/MISSING_INFORMATION.md)

## 当前可以确认什么

当天源码已补齐 NCCL 通信器初始化、成组发送接收及计算流与通信流的依赖。归档中保留了 4 个 rank 的 Nsight 报告，但缺少该阶段单独保存的正式 benchmark 文本日志。因此，本报告记录实现和已有证据，不填写无法核对的耗时或加速比。

NCCL 是 NVIDIA Collective Communications Library。这里使用的是主机发起的点对点发送与接收；GPU 执行通信工作。

## 当天完成的实现

- **通信器初始化：** 通过 MPI 分发 NCCL 标识，再建立每个 rank 对应的通信器。见 [初始化源码](archive/tasks/NCCL/jacobi.cpp#L206)。
- **边界交换：** 在 `ncclGroupStart` 与 `ncclGroupEnd` 之间安排两次发送、两次接收。见 [迭代中的交换](archive/tasks/NCCL/jacobi.cpp#L381)。
- **检查范围：** 当前快照的数值比较循环包含每个 rank 的最后一行。见 [数值比较](archive/tasks/NCCL/jacobi.cpp#L421)。这表明检查的实现范围，不能替代缺失的运行输出。

## 已保存的证据

[源码、Makefile 与练习说明](archive/tasks/NCCL/) 和名为 `jacobi.07H-NCCL-task__20261115-2147` 的 4 份 `.nsys-rep` 已保存。rank 编号为 0、1、2、3，文件清单与 SHA-256 位于公共 [profiles.csv](../../../docs/experiments/2026-11-15/data/profiles.csv)。

本次整理没有在本机打开这些 Nsight 文件，也没有重新运行 GPU 程序。文件存在和 rank 齐全只证明归档完整，不证明所有时间线特征或数值结果已经独立复核。

## 如何复查与补齐

在有课程环境和有效 GPU 资源分配时，进入源码目录，按相邻 Makefile 编译，保留完整命令、退出码、数值检查和求解时间。示例运行参数为 `srun --cpu-bind=sockets -n 4 ./jacobi -nx 16384 -ny 16384 -niter 1000 -nccheck 1`；这是一条复现建议，不是对缺失原命令的恢复。

优先补充原始终端日志，以及包含边界 kernel、内部 kernel、NCCL 通信和流编号的时间线截图。目前不适合将这个阶段加入不同通信库的速度排名。
