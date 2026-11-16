"""Rebuild the four figures from benchmarks.csv; requires matplotlib 3.11.2."""

import csv
import statistics
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    repository = Path(__file__).resolve().parents[4]
    with Path(__file__).with_name("benchmarks.csv").open() as source:
        measurements = list(csv.DictReader(source))
    plt.rcParams.update({
        "font.size": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titleweight": "bold",
        "svg.fonttype": "none",
    })
    plot_mpi(repository, measurements)
    plot_host_repeats(repository, measurements)
    plot_grouped(
        repository, measurements, "CUDA Graph", "09", "cuda-graph-priority",
        ["priority ON", "priority OFF"],
        "CUDA Graph: node-priority ON versus OFF",
        "Job 2926183 | rank 0 timing | upload ON | n = 1 per combination",
        0.52,
    )
    plot_grouped(
        repository, measurements, "NVSHMEM device", "09", "nvshmem-device-variants",
        ["scalar 32x32", "scalar 256x1", "block 256x1"],
        "NVSHMEM Device: geometry and communication variants",
        "Job 2928756 | max-rank timing | n = 1 | single-GPU reference: 32 x 32",
        0.76,
    )
    print("Rebuilt four figures in PNG and SVG format.")


def save_figure(figure, repository, chapter, filename, note):
    chapter_path = next(repository.glob(chapter + "-*"))
    output = chapter_path / "reports/2026-11-15/figures"
    output.mkdir(parents=True, exist_ok=True)
    # Fixed margins keep long notes and axis labels inside the image.
    figure.subplots_adjust(left=0.13, right=0.97, top=0.84, bottom=0.24)
    figure.text(0.13, 0.06, note, fontsize=9)
    figure.savefig(output / (filename + ".png"), dpi=130)
    figure.savefig(output / (filename + ".svg"))
    plt.close(figure)


def plot_mpi(repository, measurements):
    selected = sorted(
        [row for row in measurements if row["method"] == "MPI overlap"],
        key=lambda row: int(row["nccheck"]),
    )
    figure, axis = plt.subplots(figsize=(11, 5.5))
    bars = axis.bar(
        [row["nccheck"] for row in selected],
        [float(row["multi_gpu_s"]) for row in selected],
        color="#2869A2", width=0.58,
    )
    axis.bar_label(bars, fmt="%.4f s", padding=5)
    axis.set_ylim(0, 0.48)
    axis.set(xlabel="Norm-check interval (nccheck)", ylabel="Solver time (s)")
    axis.set_title("MPI overlap after final-synchronization timing fix", fontsize=15)
    save_figure(
        figure, repository, "04", "mpi-nccheck",
        "16384 x 16384 | 1000 iterations | rank 0 timing | n = 1 per setting | different allocations",
    )


def plot_host_repeats(repository, measurements):
    selected = [row for row in measurements
                if row["method"] == "NVSHMEM host" and row["variant"] == "controlled"]
    figure, axis = plt.subplots(figsize=(11, 5.5))
    for position, interval in enumerate(["1", "10"]):
        times = [float(row["multi_gpu_s"]) for row in selected
                 if row["nccheck"] == interval]
        median = statistics.median(times)
        axis.bar(position, median, width=0.5,
                 color=["#2869A2", "#368270"][position], alpha=0.85)
        axis.scatter([position - 0.1, position, position + 0.1], times,
                     color="#222222", zorder=3)
        axis.errorbar(position, median,
                      yerr=[[median - min(times)], [max(times) - median]],
                      fmt="none", ecolor="#111111", capsize=10, zorder=4)
        axis.text(position, max(times) + 0.018,
                  f"{median:.4f} s\n[{min(times):.4f}, {max(times):.4f}]",
                  ha="center", fontsize=11)
    axis.set_xticks([0, 1], ["1", "10"])
    axis.set_ylim(0, 0.59)
    axis.set(xlabel="Norm-check interval (nccheck)", ylabel="Solver time (s)")
    axis.set_title("NVSHMEM Host: controlled repeat measurements", fontsize=15)
    save_figure(
        figure, repository, "07", "nvshmem-host-controlled",
        "Job 2925563 | rank 0 timing | same allocation/binary/binding | n = 3 | whiskers: min-max",
    )


def plot_grouped(repository, measurements, method, chapter, filename,
                 variants, title, note, upper_limit):
    figure, axis = plt.subplots(figsize=(11, 5.5))
    colors = ["#2869A2", "#368270", "#D18B37"]
    width = 0.7 / len(variants)
    for position, variant in enumerate(variants):
        times = [
            float(next(row["multi_gpu_s"] for row in measurements
                       if row["method"] == method and row["variant"] == variant
                       and row["nccheck"] == interval))
            for interval in ["1", "10"]
        ]
        locations = [index + (position - (len(variants) - 1) / 2) * width
                     for index in range(2)]
        bars = axis.bar(locations, times, width=width,
                        label=variant, color=colors[position])
        axis.bar_label(bars, fmt="%.4f", padding=4, fontsize=10)
    axis.set_xticks([0, 1], ["1", "10"])
    axis.set_ylim(0, upper_limit)
    axis.set(xlabel="Norm-check interval (nccheck)", ylabel="Solver time (s)")
    axis.set_title(title, fontsize=15)
    axis.legend(frameon=False, ncols=len(variants), loc="upper center")
    save_figure(figure, repository, chapter, filename, note)


if __name__ == "__main__":
    main()
