# Publication review — 16 November 2026

Identify what this prepared GitHub contribution discloses and what remains local.

Date: 2026-11-16. Audience: the repository owner approving publication.

## Proposed destination

The existing local repository points to `IoriOikawa/tutorial-multi-gpu`. GitHub metadata reports that repository as public. The owner approved upload to a new public branch after personal information was removed. This package uses a new `research/2026-11-16/` path on branch `research/sc26-2026-11-16`. Repository visibility will not be changed. Existing experiment directories will not be replaced.

## Information retained

Publication includes research prose, result CSVs, relevant accepted/rejected/preliminary run logs, numerical negative controls, original analysis/resume scripts, source snapshots, patches, and hashes. Job IDs and compute-node labels remain because they identify measurements from the same allocation. Run logs also include process identifiers and CPU-binding masks. These are operational experiment metadata, not authentication credentials.

## Information excluded

Full Slurm allocation dumps contain a cluster username, numeric user/group IDs, a training account and absolute home/project paths. These dumps remain local. GPU inventories, build logs, absolute-path summary text and source-provenance text also remain local. Selected published files have no occurrences of those personal account identifiers or cluster home paths. A pattern scan for common credential formats and private keys is recorded in the local audit; pattern scans cannot prove that no secret exists.

The full ZIP and tarball, executables, object files, compiled Python caches, `.DS_Store`, AppleDouble metadata and duplicate extracted snapshots remain local. No selected evidence file needs content redaction; its SHA-256 matches its checkpoint original.

## Size and license boundary

The largest file in the full checkpoint is the Chapter09A executable at 5,228,240 bytes. No checkpoint file approaches 50 MiB. The publication omits binaries for source review and portability, even though this checkpoint is small. It does not duplicate the previous day's profiling archive.

The target repository has an MIT license. Chapter04 NVIDIA source files contain BSD redistribution conditions; Chapter09A NVIDIA source contains MIT text. Those file-level notices are preserved. The package adds no conference slides, registration documents or other unrelated course materials. See [third-party notices](THIRD_PARTY_NOTICES.md) for the source inventory.
