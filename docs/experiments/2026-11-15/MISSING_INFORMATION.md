# 需要补充的信息、实验与截图

[English](MISSING_INFORMATION.en.md) | [简体中文](MISSING_INFORMATION.md) | [日本語](MISSING_INFORMATION.ja.md)

记录日期：2026-11-15（America/Chicago）。供课后复习与复现实验使用。

本清单面向后续补资料的读者。已有原始 trace 已入仓库，下面主要需要从这些文件导出截图，或补回缺失输出；没有要求重新寻找已保存的文件。每张截图请保留 rank、时间标尺、流编号、kernel 名称及 NVTX 范围，并在说明中写原文件名和迭代窗口。

## 优先补回会影响结论的信息

- **第 04 章数值检查：** 补齐最后有效行与非有限值检查后的重跑日志。原数据保持不动。它决定“通过数值验证”可以覆盖的范围。
- **第 07 章 NCCL Host 输出：** 保存当时正式运行的完整命令、退出码、网格尺寸、迭代数、`nccheck`、数值检查和最终时间。目前只有源码与 4 个 rank 的 trace，没有可核对的正式 benchmark 文本。
- **NVSHMEM 早期异常对照：** 找回作业 2925255、`nccheck=1`、0.4770 s 对应的原日志及 placement。2.4381 s 的作业 2925303 日志已在仓库，无需再找。同作业受控复查也已保存，结果未复现旧异常。
- **NCCL Device 初次失败：** 找回第一条有效行不匹配的原始终端输出或截图。修正后的成功日志和源码已保存；初次失败目前只有当时说明。
- **NCCL 精确版本：** 补充实际使用的 `ncclGetVersion` 输出或共享库版本证据。`default-CUDA-13` 只是一项模块选择，不能替代精确库版本。

## 从已有 trace 导出这些截图

- **MPI 重叠：** 从第 04 章修正后 `nccheck10` 的 rank 0 trace 导出稳定迭代窗口，展开内部计算、边界计算和 MPI 调用。再给一个其他 rank 的同一窗口，检查是否存在等待不对称。
- **NCCL Host：** 从 `jacobi.07H-NCCL-task__20261115-2147` 导出包含计算流和通信流的窗口。说明可以看到的重叠区间；暂不填写未经统计的重叠百分比。
- **NVSHMEM Host：** 从早期 `nvshmem_overlap` 导出全部 rank 同一时间范围，展开 barrier、put/quiet 与计算。注明它与后续 6 次受控 benchmark 不是同一批运行。
- **NCCL Device LSA：** 从 `nccl-device-lsa-fix` 导出 kernel 名称、设备通信相关范围和最终同步。需要核对当时记录的 3.642 ms 主机范围与 3.627 ms GPU 投影范围；这些值尚未由本次整理独立测量。
- **CUDA Graph ON/OFF：** 从作业 2926183 的两组 trace 各选相同迭代数和相同横轴范围，展开 graph 节点，显示边界、NCCL、内部计算和检查范数的依赖。八份 trace 已保存。
- **NVSHMEM Device 三种配置：** 从作业 2928756 的 scalar、scalar-1d、block 各导出相同稳定窗口，保留 kernel 形状与 barrier；必要时再展开其余 rank。十二份 trace 已保存。

## 需要新测量才能回答的问题

匹配单 GPU kernel 后的效率、Graph 优先级的统计稳定性，以及 Host 异常的触发原因，都需要新增实验。截图不能替代这些数据。具体方法和完成条件已单列在 [后续研究问题](OPEN_QUESTIONS.md)。

## 资料覆盖与工具限制

聊天读取接口未返回附图和附件内容；报告依据实际压缩包，不推测这些附件里的结果。第 04 章较早 profile 的完整启动参数与可执行文件对应关系也未全部保留，需结合原终端记录确认。

当前整理环境没有 `nsys`，未逐个打开二进制报告或导出 GUI 截图。已有四张测量图直接从 [benchmarks.csv](data/benchmarks.csv) 的日志数据绘制，不使用示意时间线替代真实 profiling 证据。
