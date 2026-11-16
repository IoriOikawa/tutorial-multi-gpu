# 2026-11-15 SC26 多 GPU 实验记录

[English](README.en.md) | [简体中文](README.md) | [日本語](README.ja.md)

记录日期：2026-11-15（America/Chicago）。三语版整理日期：2026-11-16。供课后复习与复现实验使用。

本记录帮助课后读者查阅当天实现、实验结果及仍需验证的问题。实验对应本仓库的分布式 GPU 教程，课程入口见 [根目录 README](../../../README.zh-CN.md)。

## 今日结论

已保存当天的实现快照、6 篇英中日三语报告、22 条可读取的正式或历史 benchmark 结果，以及 56 份 Nsight Systems 报告。原课程 `tasks/` 与 `solutions/` 文件保持原样，完成版本放在各章报告的 `archive/` 中。

- **已保留的实现：** MPI 重叠、NCCL Host、NVSHMEM Host、NCCL Device 的 LSA 写入、CUDA Graph 和 NVSHMEM Device 配置。
- **已核对的后续结果：** NVSHMEM Host 受控复查未复现早期慢速；CUDA Graph 优先级只有单次对照；超过 100% 的打印效率存在参考 kernel 配置差异。
- **仍需补充：** 第 04 章最后一行与非有限值检查、NCCL Host benchmark 原始输出、相同尺度的 Nsight 截图，以及公平基准和重复测量。

本次整理仅核对已有文件、源码和算术，没有在 GPU 集群上重新编译或执行。失败运行与成功运行分开记录，短 trace 时间不作为 1000 次迭代的 benchmark。

## 查阅实验报告

- **实验报告：** [第 04 章：MPI 重叠与计时修正](../../../04-H_Overlap_Communication_and_Computation_MPI/reports/2026-11-15/README.md)
- **实验报告：** [第 07 章：NCCL Host API](../../../07-H_NCCL_NVSHMEM/reports/2026-11-15/nccl-host.md)
- **实验报告：** [第 07 章：NVSHMEM Host 与异常复查](../../../07-H_NCCL_NVSHMEM/reports/2026-11-15/nvshmem-host.md)
- **实验报告：** [第 09 章：NCCL Device LSA 写入](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nccl-device.md)
- **实验报告：** [第 09 章：CUDA Graph 节点优先级](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/cuda-graphs.md)
- **实验报告：** [第 09 章：NVSHMEM Device 三种配置](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nvshmem-device.md)

继续查看 [待补信息与截图清单](MISSING_INFORMATION.md)、[后续研究问题](OPEN_QUESTIONS.md) 和 [当天对话中的技术事项](CONVERSATION_NOTES.md)。

## 核对环境与计时口径

后续受控实验的环境记录显示：平台为课程使用的 JUPITER，Slurm 分区名称为 `booster`，GPU 型号为 NVIDIA GH200 120GB，单节点使用 4 张 GPU。编译环境记录 CUDA 13.3.33、GCC 15.2.0、Open MPI 5.0.10、NVSHMEM 3.8.0，以及 Nsight Systems 2026.6.1。NCCL 模块名为 `default-CUDA-13`；缺少已确认的精确运行时版本，不将模块名当作版本号。

`nccheck` 控制周期性范数检查；非 CSV 模式每 100 次迭代还可能执行打印所需检查。1 GPU 与 4 GPU 的打印效率计算为 `T1 / (4 × T4) × 100%`。第 04、07 章与 NCCL Device、Graph 的结果为 rank 0 时间；NVSHMEM Device 的后续实现为各 rank 时间的最大值。因此，这些表不是统一计时口径的通信库排行榜。

原文件名和日志时间保持原样。`20261116T03...Z` 是 UTC，换算到 Chicago 仍为 2026-11-15；集群终端中未注明时区的本地时间不自行重标。

## 追溯原始资料

输入为 `SC26-Multi-GPU-Tutorial_COMPLETE_20261116T041055Z.tar.gz`，SHA-256：

```text
2f6feec5cd6d83c84b7d238bc67f589f49ee284802c10347faaa5b58e577ed8b
```

[data/provenance.json](data/provenance.json) 将保存文件映射回原压缩包成员，并记录原始字节数和 SHA-256。234 份原始文件约 48 MB，按字节保留，包括 56 份二进制 trace。未重复提交可执行文件、对象文件、嵌套压缩包、无输出的 Notebook，以及仓库已有的讲义和参考解答。

- **测量表：** [benchmarks.csv](data/benchmarks.csv)，每行链接一个来源日志，区分早期异常、受控测量和计时口径。
- **运行登记：** [runs.csv](data/runs.csv)，合并 33 条原 registry 记录；包含 6 个因资源分配过期而失败的 step。没有 registry 的旧实验不补造状态。
- **Trace 清单：** [profiles.csv](data/profiles.csv)，共 14 组、56 份，逐组包含 rank 0、1、2、3。齐全只表示归档覆盖，不表示二进制内容已由本次整理逐一打开验证。

## 检查与复现

每篇报告链接了当天源码、Makefile、脚本和日志。集群脚本中的资源分配、模块和路径应按实际环境检查后使用。已有执行文件没有进入本记录；复现应从保存源码重新构建。

目录还保留原压缩包的内容、实验和 profile 清单。原始 `source.sha256` 可能列有未提交的可执行文件；核对当前附件应使用 `provenance.json` 中的路径与哈希。另见 [同日 CPU 教程资料归档](RELATED_RESOURCES.md)。完整对话未公开复制，非实验内容未纳入报告。文字按 ISO 24495 的清晰写作原则组织；这是写作方法说明，不是标准认证或实验正确性证明。

四张数据图由 [plot_results.py](data/plot_results.py) 读取 CSV 生成。绘图环境为 Matplotlib 3.11.2；已有 Python 与 Matplotlib 时，在仓库根目录运行：

```sh
python3 docs/experiments/2026-11-15/data/plot_results.py
```

三语版本的文件范围与一致性检查见 [翻译核验记录](data/translation-checks.json)。
