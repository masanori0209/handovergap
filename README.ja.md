# HandoverGap RAG

[![CI](https://github.com/masanori0209/handovergap/actions/workflows/ci.yml/badge.svg)](https://github.com/masanori0209/handovergap/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)

[English README](README.md)

最新確認済みリリース: `handovergap==0.1.13`

使い方ページ: https://masanori0209.github.io/handovergap/

HandoverGap RAG は、RAGで取得された正しい業務記憶に不足している暗黙前提を、プロファイルと作業文脈ごとに検出します。

> 正しい記憶でも、引き継げるとは限らない。

```text
A社は今回だけCSVで対応し、APIは次フェーズにする
```

この記憶は正しくても、特定のプロファイルと作業文脈で安全に使うには、顧客への説明状況、適用範囲、回答権限、代替手段、エスカレーション先が不足している可能性があります。

HandoverGapはプロファイル条件付きの文脈準備度検査を行い、不安全な転送を止め、確認質問を生成します。現在のMVPでは `CS` / `Engineer` / `Sales` を同梱データセット用の引き継ぎプリセットとして使っていますが、これは特定部門専用という意味ではなく、利用者・役割・作業文脈ごとに必要な前提が変わることを示す例です。

## HandoverGapの良さ

| 方式 | 見ているもの | 取りこぼしやすいもの |
|---|---|---|
| Naive RAG | 関連する記憶を返す | 特定プロファイルが安全に使えるか |
| Hybrid RAG | 関連証拠やリスク警告を足す | プロファイルごとの不足前提 |
| 一般的なContext Engineering | promptや文脈の渡し方を改善する | なぜ回答を止めたかの監査証跡 |
| HandoverGap RAG | 回答前に必須スロットを検査する | 本番利用には組織ごとのannotation調整が必要 |

持ち帰りポイントは4つです。

1. 正しさと引き継ぎ可能性は別に測る。
2. プロファイルと作業文脈ごとに必須スロットを定義する。
3. 不足情報を補完せず、確認質問へ変換する。
4. スロット抽出、gap、質問、transfer判断をTiDBに残す。

## クイックスタート

```bash
pip install handovergap

handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
```

TiDBアカウント、OpenAI APIキー、外部データセットは不要です。

## 実装例

既存RAGに組み込む最初の導線として、フレームワーク非依存のend-to-end例を用意しています。

```bash
python examples/end_to_end_integration.py
```

LangChain / LlamaIndex を含む組み込みパターンは [RAG Integration Recipes](docs/30_rag_integration_recipes.md) にまとめています。

この例では、既存のretrieverが返した記憶と証拠を、HandoverGapに渡すまでの流れを一通り確認できます。

1. 候補となる記憶と証拠を取得する。
2. 証拠が支えているスロットを明示する。
3. `TransferabilityGate.check(...)` で不足文脈を検査する。
4. `answer` / `ask` / `block` のプロダクト向けrouteに変換する。

最初の検索結果では代替手段とエスカレーション先が足りないため `block` になり、runbook証拠を追加すると `answer` に変わります。OpenAIによるslot fillingやTiDBへの監査保存は任意で差し替えられます。

## デモ

```bash
pip install "handovergap[demo]"
handovergap serve
```

デモは日本語がデフォルトで、英語へ切り替えられます。デフォルトの **ローカルサンプル** モードは、架空の引き継ぎケースに対して実際の決定的HandoverGap検出器を動かし、Naive RAG、Hybrid RAG、HandoverGap RAGを比較します。

OpenAIによる意味的スロット抽出とTiDBへの監査保存まで含める場合:

```bash
pip install "handovergap[live]"
handovergap serve
```

`OPENAI_API_KEY` と、`HANDOVERGAP_TIDB_URL` または `TIDB_HOST` / `TIDB_USER` / `TIDB_PASSWORD` を設定してください。**実LLM + TiDB** モードでは、選択したモデルがプロファイル別の必須スロットを埋め、その結果をHandoverGapに通し、slot fill attempt、context gap、transfer assessmentをTiDBへ保存します。

デモ内の「サポート対応」「技術運用」「商談レビュー」は、同梱プリセットを分かりやすく見せるための表示名です。HandoverGapの目的は業務分野分類ではなく、特定プロファイルが安全に行動するために必要な暗黙前提を検査することです。

データモデルは `profile` / `task_context` を正規フィールドにしています。引き継ぎは最初の利用例であり、機構としては「特定プロファイルが安全に判断するための文脈が足りているか」を見るゲートです。

![日本語Streamlitデモ](docs/assets/demo-ja.png)

## 評価結果

同梱の合成データセット20件に対する決定的評価です。

同梱データセット全体の再現可能なMarkdownレポートは次で生成できます。

```bash
handovergap report --dataset all --output reports/evaluation-latest.md
```

| 手法 | 暗黙ギャップ検出率 | 不適切転送の防止率 | 質問カバレッジ | 安全転送の許可率 | ブロック精度 | 不要確認率 |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| hybrid_rag | 0.21 | 0.59 | 0.21 | 0.67 | 0.91 | 1.00 |
| handovergap | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |

未知holdoutデータと、LLMがslotを控えめ/楽観的に埋めた場合の揺れは次で確認できます。

```bash
handovergap evaluate --dataset holdout --stress-filling
```

| 手法 | 暗黙ギャップ検出率 | 不適切転送の防止率 | 質問カバレッジ | 安全転送の許可率 | ブロック精度 | 不要確認率 |
|---|---:|---:|---:|---:|---:|---:|
| handovergap/provided | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 | 0.00 |
| handovergap/conservative | 1.00 | 0.67 | 1.00 | 0.67 | 0.67 | 1.00 |
| handovergap/optimistic | 0.64 | 0.67 | 0.64 | 1.00 | 1.00 | 0.00 |

楽観的プロファイルでは、曖昧な証拠をLLMが埋まったスロットとして扱いすぎる状況を模擬しています。この場合、検出率は落ち、不適切転送の防止率も `0.67` に留まります。

`provided_slots` と `gold_gaps` の構造的な一致を崩した adversarial split も用意しています。

```bash
handovergap evaluate --dataset adversarial --compare
```

| 手法 | 暗黙ギャップ検出率 | 不適切転送の防止率 | 質問カバレッジ | 安全転送の許可率 | ブロック精度 | 不要確認率 |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| hybrid_rag | 0.25 | 0.67 | 0.25 | 1.00 | 1.00 | 0.00 |
| handovergap | 0.38 | 0.67 | 0.38 | 1.00 | 1.00 | 0.00 |

このsplitは意図的に難しくしています。シナリオ数を増やすだけではなく、評価ラベルと検出器入力の生成経路を分離しないと本番精度の検証にならないためです。`0.1.5` では明示的な evidence slot も充足済みとして扱うようにし、adversarial の不要確認率を `0.67` から `0.00` へ下げました。ただしRecall 0.38 は残しており、過剰な成功主張にはしていません。

実データに近いが機密を含まない評価として、匿名化業務メモ風の sanitized split も追加しています。

```bash
handovergap evaluate --dataset sanitized --compare
```

| 手法 | 暗黙ギャップ検出率 | 不適切転送の防止率 | 質問カバレッジ | 安全転送の許可率 | ブロック精度 | 不要確認率 |
|---|---:|---:|---:|---:|---:|---:|
| naive_rag | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 |
| hybrid_rag | 0.71 | 0.20 | 0.71 | 1.00 | 1.00 | 0.00 |
| handovergap | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 0.00 |

sanitized split は合成データですが、匿名化済みCRMメモ、障害タイムライン、Runbook、リリースチェックリスト、商談レビューに近い書き方にしています。実会社名、従業員名、顧客名、チケット番号、アカウント情報は含めていません。

任意のOpenAI実接続スロット抽出は次で検証できます。

```bash
python harness/validation/openai_slot_filling_check.py --dataset holdout --persist-tidb
```

`gpt-4.1-mini` での観測結果は、暗黙ギャップ検出率 `0.91`、不適切転送の防止率 `0.33`、安全転送の許可率 `0.67`、ブロック精度 `0.50` でした。詳細は `article/openai_slot_filling_results.json` に保存されます。

`gpt-5-mini` での観測結果は、暗黙ギャップ検出率 `0.45`、不適切転送の防止率 `0.33`、安全転送の許可率 `0.67`、ブロック精度 `0.50` でした。使用量は入力1,901 tokens、出力8,136 tokens、うちreasoning 5,184 tokensで、推定費用は約 `$0.0167` です。この低いRecallも意図的に残しています。意味的スロット抽出はモデルとプロンプトに敏感なので、良い数値だけを見せないためです。

`gpt-5-mini` 向けに調整した `gpt5_strict` promptでは、暗黙ギャップ検出率 `1.00`、不適切転送の防止率 `0.67`、安全転送の許可率 `1.00`、ブロック精度 `1.00` でした。このpromptはholdoutの証拠要約形式に合わせて校正しているため、本番精度ではなく、モデル別prompt調整の効果として扱います。

## TiDBモード

```bash
pip install "handovergap[tidb]"
handovergap schema --dialect tidb
```

TiDB schemaは証拠、記憶、役割要件、スロット抽出試行、context gap、確認質問、transfer assessment、評価結果を保存します。

TiDBの価値はVector検索だけではありません。HandoverGapでは、回答を止めた理由をSQLで追えるように、判断過程を1つの監査ストアへ残します。

```bash
handovergap audit-sql
handovergap audit-example
handovergap audit-benchmark --dataset all --iterations 100
```

このクエリは `transfer_assessments`、`memory_items`、`context_gaps`、`slot_fill_attempts`、`source_events`、`clarification_questions` をJOINし、「記憶は取得できたが、どの必須スロットが不足し、どの証拠を確認し、何を質問すべきか」を追跡します。

`audit-example` は、ライブTiDB接続なしでblocked-transferの監査結果例を表形式で表示します。

`audit-benchmark` は、同梱シナリオから監査行をローカル生成し、行数、blocked件数、頻出不足スロット、p50/p95実行時間を表示します。これはTiDBクエリレイテンシの主張ではなく、TiDBに保存・照会する監査ワークロードの規模を見るための実測です。

実TiDB Cloudでのblocked-transfer監査クエリの検証結果:

| 項目 | 観測値 |
|---|---:|
| 投入dataset | `sanitized` |
| シナリオ | 6 |
| source events | 10 |
| slot-fill attempts | 34 |
| context gaps | 7 |
| clarification questions | 7 |
| transfer assessments | 6 |
| 監査クエリ結果行 | 7 |
| クエリ実行回数 | 10 |
| p50監査クエリlatency | `48.408 ms` |
| p95監査クエリlatency | `1510.413 ms` |

これはTiDB Cloud上の10 iteration実DB検証であり、負荷試験の主張ではありません。p95にはcold/クラウド側の揺れが含まれるため、性能ベンチではなく監査パスが実DBで動く証拠として扱います。詳細は [`article/tidb_audit_query_results.md`](article/tidb_audit_query_results.md) に保存しています。

生成ワークロードを実TiDB Cloudに投入した検証結果:

| 項目 | 観測値 |
|---|---:|
| 生成シナリオ | 100 |
| source events | 100 |
| memory chunks | 200 |
| slot-fill attempts | 567 |
| context gaps | 254 |
| clarification questions | 254 |
| transfer assessments | 100 |
| 監査クエリ結果行 | 254 |
| クエリ実行回数 | 10 |
| p50監査クエリlatency | `38.818 ms` |
| p95監査クエリlatency | `574.713 ms` |

生成ワークロードの実TiDB検証では、10,000シナリオをmemory chunk込みで保存し、25,007件のblocked-transfer監査行をJOINできることを確認しました。

| 項目 | 観測値 |
|---|---:|
| 生成シナリオ | 10,000 |
| source events | 10,000 |
| memory chunks | 20,000 |
| slot-fill attempts | 56,667 |
| context gaps | 25,007 |
| clarification questions | 25,007 |
| transfer assessments | 10,000 |
| 監査クエリ結果行 | 25,007 |
| クエリ実行回数 | 10 |
| p50監査クエリlatency | `1374.01 ms` |
| p95監査クエリlatency | `1478.298 ms` |

無料枠のストレージを守るため、100,000シナリオではVECTOR/full-text chunkを省いた監査テーブル中心の検証を行いました。

| 項目 | 観測値 |
|---|---:|
| 生成シナリオ | 100,000 |
| source events | 100,000 |
| memory chunks | 0 |
| slot-fill attempts | 566,667 |
| context gaps | 250,004 |
| clarification questions | 250,004 |
| transfer assessments | 100,000 |
| 監査クエリ結果行 | 250,004 |
| クエリ実行回数 | 10 |
| p50監査クエリlatency | `14236.62 ms` |
| p95監査クエリlatency | `15074.449 ms` |

10k/100kの詳細は [`article/tidb_workload_audit_10k_results.md`](article/tidb_workload_audit_10k_results.md) と [`article/tidb_workload_audit_100k_results.md`](article/tidb_workload_audit_100k_results.md) に保存しています。これは監査経路が実DBで動くことの確認であり、負荷性能の主張ではありません。

Slackで観測した引き継ぎに近い公開チャンネル上のやり取りから、原文・氏名・顧客名・URL・IDを保存せず、パターン要約だけを使った独立ラベルレビューも追加しました。結果は [`article/independent_gap_label_review.md`](article/independent_gap_label_review.md) に保存しています。

### TiDB実接続の検証

TiDB Cloudでクラスタを作成したあと、**Connect**を開き、Public接続とPython/SQLAlchemy互換の接続情報を取得します。パスワードを生成またはリセットし、ローカルでは次のように環境変数へ入れてください。

```bash
export TIDB_HOST="..."
export TIDB_PORT="4000"
export TIDB_USER="..."
export TIDB_PASSWORD="..."
export TIDB_DB_NAME="test"
export TIDB_CA_PATH="/path/to/ca-certificates.crt"
```

その後、次を実行します。

```bash
python harness/validation/tidb_live_check.py --reset-schema
python harness/validation/tidb_audit_query_check.py --reset-schema --dataset sanitized --iterations 10
```

この検証はschemaを作り直し、合成memoryと証拠、スロット抽出試行、context gap、transfer assessment、評価結果を保存して、件数をJSONで出力します。`--reset-schema` は同梱HandoverGapテーブルを削除して作り直すため、ユーザーデータの無いα版検証DBでのみ使ってください。`.env`やTiDB認証情報はコミットしないでください。

## 制約

- MVPの検出器とbaselineは決定的ルールです。
- HandoverGapBench miniとholdoutは合成データです。sanitized splitは実務メモに近い形ですが、機密を含まない合成データです。
- 必須スロットとgold gapが構造的に揃っている限り、シナリオ数を増やすだけでは本番精度の証明にはなりません。独立annotationが次の課題です。
- スロット抽出のstress profileはLLMの揺れを模擬するもので、実LLM評価の代替ではありません。
- OpenAI実接続スロット抽出は任意で、初回利用には不要です。
- OpenAI実接続スロット抽出はモデル依存で、現在のholdoutでは `gpt-4.1-mini` と `gpt-5-mini` の結果が大きく異なります。
- Streamlitデモは架空の引き継ぎケースを使います。実LLMモードではOpenAIスロット抽出とTiDB監査保存を実行しますが、本番検索サービスではなくローカルデモです。
- 質問の意味的同値判定は未実装です。
- ライブTiDB接続はoptional dependencyです。

## 開発

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,demo]"
.venv/bin/pytest
```

## ライセンス

MIT
