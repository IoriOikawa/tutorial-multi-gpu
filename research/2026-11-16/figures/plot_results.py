"""Plot the 64 primary measurements. Requires Matplotlib."""
from pathlib import Path
from statistics import median
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "chapter09a-nvshmem/summary/20261116T155724Z/benchmark_results.csv").open() as stream:
    rows = list(csv.DictReader(stream))
assert len(rows) == 64
fig, axes = plt.subplots(1, 3, figsize=(13, 4.3), layout="constrained")
for axis, metric, title, ylabel in zip(
    axes,
    ("ref_sec", "parallel_sec", "efficiency"),
    ("Single-GPU reference", "Four-GPU solver", "Reported efficiency"),
    ("Median runtime (s)", "Median runtime (s)", "Median efficiency (%)"),
):
    for interval, offset, color in [(1, -0.19, "#3b6fa3"), (10, 0.19, "#bc692b")]:
        values = []
        for mode in "ABCD":
            samples = [float(r[metric]) for r in rows if r["config"] == mode and int(r["nc"]) == interval]
            assert len(samples) == 8
            values.append(median(samples))
        bars = axis.bar([i + offset for i in range(4)], values, width=0.36, label=f"nccheck={interval}", color=color)
        axis.bar_label(bars, fmt="%.2f" if metric == "efficiency" else "%.3f", fontsize=8, padding=3)
    axis.set(title=title, ylabel=ylabel, xticks=range(4), xticklabels=list("ABCD"))
    axis.set_ylim(0, max(p.get_height() for p in axis.patches) * 1.22)
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", alpha=0.18)
    axis.set_axisbelow(True)
    axis.legend(frameon=False, fontsize=8)
axes[2].axhline(100, color="#555555", linestyle="--", linewidth=0.9)
fig.suptitle("NVSHMEM matched geometry · 64 primary measurements · 8 per group", fontsize=13)
fig.savefig(ROOT / "figures/matched-geometry.png", dpi=170)
