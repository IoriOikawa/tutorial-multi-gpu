# 第 09 章：补齐 NCCL Device API 的 LSA 边界写入

记录日期：2026-11-15（America/Chicago）。供课后复习与复现实验使用。

[返回当天实验索引](../../../docs/experiments/2026-11-15/README.md) · [查看待补信息与截图清单](../../../docs/experiments/2026-11-15/MISSING_INFORMATION.md)

## 结论与范围

当天实现补齐了 load/store-accessible（LSA，可直接加载和存储）路径的远端写入，以及主机和设备侧的一致路径选择。修正后的 4 GPU 日志输出数值检查后的程序汇总，求解时间为 0.4340 s。

归档说明记载，早期实现曾在各 rank 第一条有效行上数值检查失败。但初次失败的完整终端日志未找到，因此本报告将其作为当时的调试记录，与保存下来的修正后日志分开叙述。这是课程练习实现的补全，不能据此认定 NCCL 库存在缺陷。

## 源码中的原因与改动

原 fork 练习文件的 LSA 分支是待完成位置，且路径选择默认返回 false。当天代码按下列顺序处理可通过 LSA 访问的 peer：

```mermaid
flowchart LR
    A[对端 world rank] --> B[转换为 LSA team rank]
    B --> C[取得远端对称窗口地址]
    C --> D[活动线程写入对应 halo 元素]
```

图描述源码中的地址转换与写入流程，不代表实测 GPU 调度时间。源码见 [路径选择](archive/tasks/results/nccl-device-lsa-fix_20261115T223202Z/source/jacobi_kernels.cu#L130)、[LSA 远端写入](archive/tasks/results/nccl-device-lsa-fix_20261115T223202Z/source/jacobi_kernels.cu#L159) 和 [主机侧选择](archive/tasks/results/nccl-device-lsa-fix_20261115T223202Z/source/jacobi_kernels.cu#L263)。

## 修正后实验结果

| 配置 | nccheck | 1 GPU / s | 4 GPU / s | 程序打印效率 / % |
|---|---:|---:|---:|---:|
| LSA fix | 1 | 1.4703 | 0.4340 | 84.70 |

原始 [benchmark.log](archive/tasks/results/nccl-device-lsa-fix_20261115T223202Z/logs/benchmark.log) 对应作业 2925699，节点 jpbo-001-09，16384×16384 网格，1000 次迭代，`nccheck=1`。表中为程序打印的 rank 0 求解时间；只有一次正式测量，不用于与其他作业的实现排名。

另外保存了一组 10 次迭代、`nccheck=10` 的 4-rank trace。该 trace 与上表 1000 次迭代的 benchmark 分开保存。

## 已有时间线观察与待补截图

当时的 [实验说明](archive/tasks/results/nccl-device-lsa-fix_20261115T223202Z/README.md) 记录 rank 0 的主机求解范围约 3.642 ms、GPU 投影范围约 3.627 ms，且未见独立 halo PtoP memcpy。这些是归档中的观察，本次整理未用 Nsight 工具独立复测。

该现象与 kernel 内远端 store 的实现一致，但不能单独证明通信已被完全隐藏。需要补充带时间标尺、kernel 名称、流编号和 NVTX 范围的截图，以及初次失败的日志或截图。
