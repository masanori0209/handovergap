# HandoverGap RAG

[![CI](https://github.com/masanori0209/handovergap/actions/workflows/ci.yml/badge.svg)](https://github.com/masanori0209/handovergap/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)

[English README](README.md)

HandoverGap RAG は、RAGで取得された正しい業務記憶に不足している暗黙前提を、引き継ぎ先の役割ごとに検出します。

> 正しい記憶でも、引き継げるとは限らない。

```text
A社は今回だけCSVで対応し、APIは次フェーズにする
```

この記憶は正しくても、CS担当者が安全に回答するには、顧客への説明状況、適用範囲、回答権限、代替手段、エスカレーション先が不足している可能性があります。

HandoverGapは役割条件付きslot検査を行い、不安全な転送を止め、確認質問を生成します。

## クイックスタート

```bash
pip install handovergap

handovergap demo
handovergap detect --scenario S001 --role CS
handovergap evaluate --compare
```

TiDBアカウント、OpenAI APIキー、外部データセットは不要です。

## デモ

```bash
pip install "handovergap[demo]"
handovergap serve
```

デモは日本語がデフォルトで、英語へ切り替えられます。Naive RAG、Hybrid RAG、HandoverGap RAGを同じ記憶で比較します。

![日本語Streamlitデモ](docs/assets/demo-ja.png)

## 評価結果

同梱の合成データセット20件に対する決定的評価です。

| 手法 | 暗黙ギャップ検出率 | 不適切転送の防止率 | 質問カバレッジ |
|---|---:|---:|---:|
| naive_rag | 0.00 | 0.00 | 0.00 |
| hybrid_rag | 0.26 | 0.59 | 0.26 |
| handovergap | 1.00 | 1.00 | 1.00 |

この結果はMVPの整合性検査であり、未知データや実環境での一般性能を意味しません。

## TiDBモード

```bash
pip install "handovergap[tidb]"
handovergap schema --dialect tidb
```

TiDB schemaは証拠、記憶、役割要件、slot fill試行、context gap、確認質問、transfer assessment、評価結果を保存します。

## 制約

- MVPの検出器とbaselineは決定的ルールです。
- HandoverGapBench miniは合成データです。
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
