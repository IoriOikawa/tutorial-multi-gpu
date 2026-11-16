# 2026-11-15 SC26 マルチ GPU 実験記録

[English](README.en.md) | [简体中文](README.md) | [日本語](README.ja.md)

記録日：2026-11-15（America/Chicago）。翻訳日：2026-11-16。講習後の復習と実験の再現に使う資料です。

この記録は、講習後の読者が当日の実装、実験結果、今後検証すべき問題を確認するためのものです。実験は本リポジトリの分散 GPU チュートリアルに対応します。講習の入口は [ルートの README](../../../README.ja.md) を参照してください。

## 当日の結論

当日の実装スナップショット、3 言語で読める 6 本の実験報告、読み取り可能な正式または過去の benchmark 結果 22 件、Nsight Systems レポート 56 件を保存しました。元の講習用 `tasks/` と `solutions/` は変更せず、完成版を各章の報告の `archive/` に置いています。

- **保存した実装：** MPI の計算と通信の重なり、NCCL Host、NVSHMEM Host、NCCL Device の LSA 書き込み、CUDA Graph、NVSHMEM Device の各構成。
- **確認した追加結果：** NVSHMEM Host の条件をそろえた再確認では、初期の低速な結果を再現できませんでした。CUDA Graph の優先度比較は単回測定です。100% を超える表示効率には、基準 kernel の構成の違いがあります。
- **追加が必要な情報：** 第 04 章の最終行と非有限値の検査、NCCL Host benchmark の元出力、同じ時間尺度の Nsight スクリーンショット、公平な基準と反復測定。

今回の整理で確認したのは既存ファイル、ソースコード、算術だけです。GPU クラスタで再コンパイルや再実行はしていません。失敗した実行と成功した実行は分けて記録し、短い trace の時間を 1000 回反復の benchmark として扱っていません。

## 実験報告を読む

- **実験報告：** [第 04 章：MPI の計算と通信の重なりと計時の修正](../../../04-H_Overlap_Communication_and_Computation_MPI/reports/2026-11-15/README.ja.md)
- **実験報告：** [第 07 章：NCCL Host API](../../../07-H_NCCL_NVSHMEM/reports/2026-11-15/nccl-host.ja.md)
- **実験報告：** [第 07 章：NVSHMEM Host と異常の再確認](../../../07-H_NCCL_NVSHMEM/reports/2026-11-15/nvshmem-host.ja.md)
- **実験報告：** [第 09 章：NCCL Device の LSA 書き込み](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nccl-device.ja.md)
- **実験報告：** [第 09 章：CUDA Graph のノード優先度](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/cuda-graphs.ja.md)
- **実験報告：** [第 09 章：NVSHMEM Device の 3 構成](../../../09-H_Device-initiated_Communication_and_CUDA_Graphs/reports/2026-11-15/nvshmem-device.ja.md)

続けて [不足情報とスクリーンショットの一覧](MISSING_INFORMATION.ja.md)、[今後の研究課題](OPEN_QUESTIONS.ja.md)、[当日の対話に含まれる技術事項](CONVERSATION_NOTES.ja.md) を参照してください。

## 環境と計時の定義を確認する

後続の条件をそろえた実験では、講習で使う JUPITER を使用しています。Slurm パーティション名は `booster`、GPU は NVIDIA GH200 120GB で、単一ノードの 4 GPU を使いました。コンパイル環境の記録は CUDA 13.3.33、GCC 15.2.0、Open MPI 5.0.10、NVSHMEM 3.8.0、Nsight Systems 2026.6.1 です。NCCL のモジュール名は `default-CUDA-13` です。正確なランタイムのバージョンは未確認のため、モジュール名をバージョン番号として扱いません。

`nccheck` は定期的なノルム確認間隔を制御します。非 CSV モードでは、100 回反復するごとの表示用にも確認を実行する場合があります。1 GPU と 4 GPU の表示効率は `T1 / (4 × T4) × 100%` で計算します。第 04、07 章と NCCL Device、Graph の結果は rank 0 の時間です。NVSHMEM Device の後続実装は各 rank の時間の最大値です。このため、これらの表は計時の定義を統一した通信ライブラリの順位表ではありません。

元のファイル名とログ時刻はそのまま残しています。`20261116T03...Z` は UTC で、Chicago 時間では 2026-11-15 です。クラスタ端末のタイムゾーン表記がないローカル時刻に、推測でタイムゾーンを付けていません。

## 元資料をたどる

入力は `SC26-Multi-GPU-Tutorial_COMPLETE_20261116T041055Z.tar.gz` です。SHA-256 は次のとおりです。

```text
2f6feec5cd6d83c84b7d238bc67f589f49ee284802c10347faaa5b58e577ed8b
```

[data/provenance.json](data/provenance.json) は、保存したファイルを元の圧縮ファイル内の項目に対応付け、元のバイト数と SHA-256 を記録しています。元ファイル 234 件、約 48 MB をバイト単位で保持しており、バイナリ trace 56 件を含みます。実行ファイル、オブジェクトファイル、入れ子の圧縮ファイル、出力のない Notebook、リポジトリに既にある講義資料と参考解答は重複して追加していません。

- **測定表：** [benchmarks.csv](data/benchmarks.csv)。各行から出典ログにリンクし、初期の異常、条件をそろえた測定、計時の定義を区別します。
- **実行台帳：** [runs.csv](data/runs.csv)。元の registry 33 件を統合しています。リソース割り当ての期限切れで失敗した step 6 件も含みます。registry のない過去の実験に状態を作り足していません。
- **Trace 一覧：** [profiles.csv](data/profiles.csv)。14 組、計 56 件で、各組に rank 0、1、2、3 があります。すべてそろっていることは保存範囲を示すだけで、今回の整理でバイナリ内容を 1 件ずつ開いて検証したことは意味しません。

## 確認と再現

各報告は当日のソースコード、Makefile、スクリプト、ログにリンクしています。クラスタ用スクリプトのリソース割り当て、モジュール、パスは、実際の環境に合わせて確認してから使ってください。既存の実行ファイルはこの記録に含めていません。再現時は保存したソースコードからビルドしてください。

このディレクトリには、元の圧縮ファイルの内容一覧、実験一覧、profile 一覧も残しています。元の `source.sha256` は、追加していない実行ファイルを含む場合があります。現在の添付ファイルの確認には `provenance.json` のパスとハッシュを使ってください。[同日に整理した CPU チュートリアル資料](RELATED_RESOURCES.ja.md) も参照できます。対話全文は公開コピーせず、実験以外の内容は報告に含めていません。文章は ISO 24495 の明確な文章作成の原則に沿って構成しています。これは執筆方法の説明であり、規格認証や実験の正しさの証明ではありません。

4 枚のデータ図は [plot_results.py](data/plot_results.py) が CSV を読み取って生成します。作図環境は Matplotlib 3.11.2 です。Python と Matplotlib があれば、リポジトリのルートで次を実行できます。

```sh
python3 docs/experiments/2026-11-15/data/plot_results.py
```

三言語版の対象ファイルと整合性の確認結果は、[翻訳検査の記録](data/translation-checks.json)を参照してください。
