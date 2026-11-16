# Archive and report verification

[English](VERIFICATION.en.md) | [简体中文](VERIFICATION.md) | [日本語](VERIFICATION.ja.md)

Record date: 2026-11-15 (America/Chicago). Explains what the archive review actually checked so readers can verify it. English translation: 2026-11-16.

## Checks performed

- **Input checksum:** The archive SHA-256 matched the supplied checksum file.
- **Attachment verification:** Sizes and SHA-256 hashes for all 234 copied files matched the original archive contents.
- **Measurement sources:** All 22 benchmark rows were checked against their original logs. Short traces and invalid jobs were excluded.
- **Run status:** The merged registry contains 33 steps, retaining all 6 failed steps. Six small-grid smoke tests are marked PASS.
- **Trace coverage:** The 56 files form 14 groups. Each group contains exactly ranks 0, 1, 2, and 3. This review did not open and parse every binary file.
- **Links and references:** The initial Chinese archive audit found all 86 local link targets and source line references in the reports and index. This is the historical audit count, not the count for today's translation checks.
- **Figures:** The plotting script succeeded and generated PNG and SVG files for all 4 figures. Key figures were visually checked for labels and spacing. Data comes from the verified CSV.
- **Arithmetic:** The single Graph interval-10 observation reduced elapsed time by 4.3150%, rounded to 4.32% in the report. Controlled Host medians were 0.4767 s and 0.3281 s.

## Limits of verification

This review environment has neither the course cluster's GPU runtime environment nor `nsys`. Historical GPU programs were therefore not rebuilt or run. Not all timeline observations were independently checked, and missing benchmarks were not filled in. Gaps in the original numerical checks and unfair references remain report limitations.

Source, scripts, notes, and logs in `archive/` are preserved as historical evidence. Their instructions were not executed automatically. The original `source.sha256` may reference executables that were not committed. Use `data/provenance.json` to verify the currently copied files.
