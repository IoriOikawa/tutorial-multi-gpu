"""Regenerate the two descriptive analysis CSVs using Python's standard library.

Only primary measurements are used. Quartiles are inclusive; pairs must share
repetition, allocation and node. These summaries are not confidence intervals.
"""
from pathlib import Path
from statistics import median, quantiles
import csv


def main():
    output = Path(__file__).resolve().parent
    source = output.parent / "chapter09a-nvshmem/summary/20261116T155724Z/benchmark_results.csv"
    with source.open() as stream:
        rows = list(csv.DictReader(stream))
    cases = {(row["config"], row["nc"], row["rep"]) for row in rows}
    if len(rows) != 64 or len(cases) != 64:
        raise ValueError("Expected 64 unique primary cases; use the archived primary CSV.")

    summaries, paired = [], []
    for interval in (1, 10):
        for mode in "ABCD":
            group = [row for row in rows if row["config"] == mode and int(row["nc"]) == interval]
            if len(group) != 8:
                raise ValueError("Expected eight primary measurements per mode and interval.")
            result = {"config": mode, "nc": interval, "n": len(group)}
            for metric in ("ref_sec", "parallel_sec", "efficiency"):
                values = [float(row[metric]) for row in group]
                first, _, third = quantiles(values, n=4, method="inclusive")
                result.update({f"{metric}_median": median(values), f"{metric}_q1": first, f"{metric}_q3": third})
            summaries.append(result)

        baseline = [row for row in rows if row["config"] == "B" and int(row["nc"]) == interval]
        matched = {pair_key(row): row for row in rows if row["config"] == "C" and int(row["nc"]) == interval}
        pairs = [(row, matched[pair_key(row)]) for row in baseline if pair_key(row) in matched]
        if len(pairs) != 8:
            raise ValueError("Expected eight B/C pairs sharing repetition, allocation and node.")
        paired.append({
            "nc": interval,
            "n_pairs": len(pairs),
            "pair_key": "rep+job_id+node",
            "reference_change_pct_median": median(100 * (float(new["ref_sec"]) / float(old["ref_sec"]) - 1) for old, new in pairs),
            "parallel_change_pct_median": median(100 * (float(new["parallel_sec"]) / float(old["parallel_sec"]) - 1) for old, new in pairs),
        })

    write_csv(output / "primary_summary.csv", summaries)
    write_csv(output / "paired_geometry.csv", paired)
    print("Regenerated primary_summary.csv and paired_geometry.csv from 64 primary measurements.")


def pair_key(row):
    return row["rep"], row["job_id"], row["node"]


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
