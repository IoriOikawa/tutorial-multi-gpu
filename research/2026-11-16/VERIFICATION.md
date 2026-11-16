# Archive verification — 16 November 2026

Record the checks that connect the publication copy to the preserved research evidence.

Date: 2026-11-16. Audience: experiment reviewers and future maintainers.

## Archive integrity

The locally available `SC26.zip` passed ZIP CRC verification for all 562 entries, including macOS metadata. Its SHA-256 is `4daf66aff914ac2049865780b751f33665565cc504103b4f9ae7203955354f17`.

The inner checkpoint archive passed its supplied SHA-256 check: `a92ced0fd91678a69e700d73fb7a46885aee66e195533aa5b17a76433d13f921`. It has 255 directory/file entries. Extraction rejected absolute paths, traversal paths and non-file/non-directory members. The supplied checkpoint inventory and the duplicate extracted checkpoint in the ZIP are checked separately in the local audit.

All 20 entries in six embedded source/build hash manifests match archived bytes. Original-source manifests were checked against their `original/` or `source/` directories; build manifests were checked against the corresponding build directories. Executables were hashed but not executed.

## Numerical and dataset checks

Chapter04 has six baseline and six overlap positive logs. Each reports PASS, complete expected coverage, zero non-finite values, zero mismatches and zero maximum absolute error. Three negative controls report FAIL and process exit code 1: NaN and Inf produce one non-finite value; the finite injection produces one mismatch. The separate failed preliminary baseline smoke log is retained and is not a positive test.

Chapter09A has 64 distinct planned `(mode, interval, repetition)` cases, nine extra accepted repetitions, three rejected benchmark logs, and zero missing cases. The supplied summarizer was executed in the publication copy. All six regenerated CSV tables match the archived parsed rows, including row order, rejection reasons and primary/extra selection. The eight smoke logs are separate from the benchmark dataset.

Every accepted CSV timing was compared with its `MATCHED_RESULT` log line. Each reported efficiency agrees with `25 × ref_sec / parallel_sec` within 0.00001 percentage points. The summarizer verifies method, reference geometry, grid size, iteration counts, four PEs, validation coverage, finite errors/timings, and completion markers where required.

All three retained change sets were applied in temporary files. Chapter04 overlap, Chapter04 baseline and Chapter09A matched-geometry patches reproduce the corresponding validated source files byte for byte. Source files include their original license notices.

## Verify the publication copy

Run from this directory:

```sh
shasum -a 256 -c SHA256SUMS
cd chapter09a-nvshmem/work
python3 ../summarize_matched.py
```

`SHA256SUMS` covers all publication files except itself. `evidence-map.csv` records unchanged evidence files copied from the checkpoint. The original research log is separately identified in `provenance.json`. Fresh summary output is derived data and is not part of the original manifest.

These are archive and analysis checks. They do not establish historical executable provenance beyond matching the supplied hashes, and they do not constitute a fresh GPU execution, compiler validation or profiling experiment.

## Trilingual integration and descriptive statistics

The follow-up integration adds equivalent [English](README.en.md), [Simplified Chinese](README.md) and [Japanese](README.ja.md) research indices and findings. It compares the old questions and missing-information checklist at `9cccb76` with evidence preserved in `e1985a0`. Both broader questions remain partial; single-row subdomains and same-implementation 1 PE/4 PE scaling are not claimed as tested.

Run `python3 analysis/summarize_primary.py` from this directory to regenerate the two new analysis CSVs. Quartiles use `statistics.quantiles(n=4, method='inclusive')`; B/C pairs share repetition, job and node. An independent NumPy percentile calculation agrees with all 72 median/quartile statistics. Both paired rows were independently checked. The generated tables are descriptive summaries, not confidence intervals.

All 197 mapped checkpoint evidence files and the author's original log retain their original SHA-256 hashes. New links and source-line targets, three-language result tables and privacy patterns were checked before integration. The [translation and integration check record](analysis/translation-checks.json) identifies the checks and document coverage. The publication manifest is regenerated for these added documents and derived tables; the original evidence map remains unchanged.
