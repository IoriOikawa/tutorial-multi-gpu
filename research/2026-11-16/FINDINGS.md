# 研究发现与既有问题完成情况

[English](FINDINGS.en.md) | [简体中文](FINDINGS.md) | [日本語](FINDINGS.ja.md)

对照主分支 11 月 15 日的问题与缺失信息清单，判断 11 月 16 日证据回答了什么。

日期：2026-11-16。读者：复核研究结论与安排后续实验的研究者。

## 概览

末行/非有限值验证缺陷及参考几何解释已有直接证据。原始问题范围更广，因此 Q1、Q4 仍为部分完成，Q2、Q3 仍未解决。Chapter04 修正验证后的重跑日志已补齐已测范围；其他旧输出、精确 NCCL 运行时版本和六类截图仍缺失。[研究索引](README.md)提供原始日志、数据和复现命令。

对照基线为提交 `9cccb76`，保留的研究 checkpoint 为提交 `e1985a0`。以下 ID 按原节与条目顺序编号，[结构化状态](analysis/question_status.json)记录其映射。表格按 GitHub 桌面文档视图阅读。

## Chapter04 在已测范围内解决验证缺陷

[overlap 验证器](chapter04-mpi-validation/work/jacobi.cpp#L595)与[baseline 验证器](chapter04-mpi-validation/baseline_strict/work/jacobi.cpp#L333)包含各 rank 最后拥有的行，拒绝参考值或计算值中的非有限值，并汇总覆盖和错误计数。在最后拥有行注入的 [NaN](chapter04-mpi-validation/negative_control/nan.log)、[Inf](chapter04-mpi-validation/negative_control/inf.log)及[有限错误](chapter04-mpi-validation/negative_control/finite.log)均被拒绝，进程退出码为 1。

[验证表](chapter04-mpi-validation/validation_results.csv)包含 baseline 和 overlap 各 6 项通过记录。测试覆盖非整除分区（`nx=261`、`ny=259`、四 rank）、3/4 次迭代与稀疏检查，包括运行 10 次迭代而 `nccheck=20`。大网格逐点检查全部 268,369,924 个内部元素，最大绝对误差为零。

单行子域尚未覆盖：小网格每个 rank 仍拥有 64 或 65 行。初始失败的 baseline smoke 日志单独保留，不算入 12 项通过测试。大网格 1,000 次迭代的 baseline/overlap 耗时在间隔 1 时为 0.4832/0.4085 s，在间隔 10 时为 0.3998/0.3130 s。它们来自不同作业和节点，不构成受控重复加速比对照。

## Chapter09A 解释已测条件下的表观超线性效率

NVSHMEM 是 NVIDIA 的共享内存通信库；本实验中一个处理单元（PE）对应一个 GPU 进程。`nccheck` 为周期范数检查间隔。全部有效分布式 benchmark 使用四 PE、16,384×16,384 网格和 1,000 次迭代。共有 64 项主测量（每种模式/间隔 8 项）、9 项额外重复、独立的 8 项 smoke 测试和 3 项排除 benchmark 日志，涉及五个 allocation、四台节点。分配覆盖不均；8 项测量不等于 8 次独立 allocation。[分配统计](chapter09a-nvshmem/summary/20261116T155724Z/summary_by_allocation.csv)保留了这一差别。

| 模式 | 纯 CUDA 参考 | 四 PE 求解器 |
|---|---|---|
| A | 32×32 | Scalar 2D |
| B | 32×32 | Scalar 1D |
| C | 256×1 | Scalar 1D |
| D | 256×1 | Block-cooperative put |

[matched-geometry 补丁](chapter09a-nvshmem/matched_geometry.patch)使参考几何可选。73 项有效测量均通过完整内部网格严格验证，参考与分布式端各执行 1,000 次迭代。主样本优先原运行，否则选最早有效补跑，不按最快耗时挑选。

| nccheck | 模式 | 参考中位数 / s | 四 PE 中位数 / s | 效率中位数 / % |
|---|---|---:|---:|---:|
| 1 | A | 1.680691 | 0.485778 | 86.4564 |
| 1 | B | 1.678612 | 0.595553 | 70.4821 |
| 1 | C | 2.156206 | 0.596066 | 90.9742 |
| 1 | D | 2.153060 | 0.596093 | 90.2988 |
| 10 | A | 1.235957 | 0.330905 | 93.4309 |
| 10 | B | 1.236389 | 0.292782 | 105.5985 |
| 10 | C | 1.088770 | 0.292753 | 92.8498 |
| 10 | D | 1.089082 | 0.297566 | 91.5239 |

报告效率为 `100 × ref_sec / (4 × parallel_sec)`，分布式耗时取各 rank 最大值。已记录的 `ref_max_sec` 不用于此效率。每列独立求中位数，因此效率中位数未必等于两列耗时中位数的比值。

间隔 10 时，B→C 的参考中位数变化 −11.940%，分布式中位数变化 −0.010%，效率从 105.5985% 降至 92.8498%。按重复编号、作业和节点匹配的 8 对 B/C 样本，其参考变化中位数为 −11.939%，分布式变化为 +0.004%。这些对照支持参考几何解释表观超线性效率。纯 CUDA 参考仍不等于同一 NVSHMEM 实现的 1 PE 基准。

间隔 1 时，256×1 参考比 32×32 慢 28.452%，性能排序反转。额外归约/原子操作开销仍是假说，需要分别 profile 启用和禁用范数计算的 kernel。间隔 10 时，D 的分布式中位耗时比 C 高约 1.64%；这一描述性差异不证明 block put 的一般优势或统计显著性。

[四分位数表](analysis/primary_summary.csv)只使用主样本，方法为 `statistics.quantiles(n=4, method='inclusive')`。间隔 10 时，B 的分布式 Q1/Q3 为 0.292439/0.293538 s，C 为 0.292719/0.293231 s。这些汇总描述区间与[配对中位数](analysis/paired_geometry.csv)不是置信区间、独立 allocation 复现或因果机制证明。

## 逐项对照原研究问题

| ID | 原任务 | 2026-11-16 状态 | 剩余工作 |
|---|---|---|---|
| Q1 | 匹配参考与强扩展 | 部分完成：几何子问题已有回答，重复结果已保存 | 同实现 1 PE/4 PE；完整基准等价性控制与不确定性 |
| Q2 | Graph 优先级稳定收益 | 未解决：没有新增 ON/OFF 数据 | 受控重复优先级对照 |
| Q3 | 早期 NVSHMEM Host 慢速 | 未解决：Device 测量没有测试 Host 异常 | 触发条件、placement/环境与受控复现 |
| Q4 | 补齐 Chapter04 检查 | 部分完成：末行/非有限值修正与 12/3 测试已核实 | 单行子域；同 allocation 重复性能对照 |

[更新后的问题清单](../../docs/experiments/2026-11-15/OPEN_QUESTIONS.md)保留剩余完成条件。已测试缺陷在研究快照中解决；原课程 `tasks/`、`solutions/` 没有被这些快照替换。

## 对照缺失信息并保留下一步

| ID | 缺失资料 | 状态 |
|---|---|---|
| M1 | Chapter04 修正验证后的重跑日志 | 已补已测范围；单行覆盖仍属于 Q4 |
| M2 | NCCL Host 正式输出 | 仍缺失 |
| M3 | Host 旧作业 2925255 日志与 placement | 仍缺失 |
| M4 | NCCL Device 原始首次失败输出 | 仍缺失 |
| M5 | 当时实验实际加载的 NCCL 精确版本 | 仍缺失；CI 镜像版本不能恢复历史运行时证据 |
| T1–T6 | MPI、NCCL Host、NVSHMEM Host、NCCL Device LSA、Graph、NVSHMEM Device 截图 | 全部待补；新性能柱状图不能替代 trace 截图 |

未返回的旧附件及较早 Chapter04 profile 启动参数/可执行映射仍是历史缺口，见[更新后的缺失信息清单](../../docs/experiments/2026-11-15/MISSING_INFORMATION.md)。后续测量宜先补单行子域和同实现强扩展，再隔离范数/归约成本。本次合并未产生新的 GPU 执行或 profiler 截图；原证据、失败日志和用户原文保持不变。
