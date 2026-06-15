# Zenn Article Outline

# 正しい記憶でも、引き継げるとは限らない：TiDBで作る HandoverGap RAG

## はじめに

- RAGは正しい情報を返せる
- でも業務引き継ぎでは、それだけでは足りない
- 正しいが引き継げない記憶がある

## 例: 「今回だけCSV」

- Naive RAGはそのまま答える
- でも顧客対応を引き継ぐには情報が足りない

## valid-but-non-transferable memory

- 正しい
- 関連している
- 矛盾していない
- でも他者が安全に使うには暗黙前提が足りない

## Tacit Context Gap

- scope_gap
- rationale_gap
- trigger_gap
- authority_gap
- exception_gap
- communication_gap
- fallback_gap

## HandoverGap RAG

- memory type classification
- successor responsibility profile requirements
- semantic slot filling
- evidence retrieval
- gap detection
- clarification questions

## TiDBを使う理由

- Vector Storeではなくスロット、証拠、gapの監査ストア
- SQL + Vector + Full-text + JSON + Transaction
- スロット抽出の過程を保存できる
- blocked transferから不足スロット、証拠、確認質問までJOINして追える

## 実装

- schema
- CLI
- detect
- evaluate
- Streamlit demo

## HandoverGapBench mini

- dataset format
- scenarios
- gold gaps
- evaluation metrics

## 比較実験

- Naive RAG
- Hybrid RAG
- HandoverGap RAG

## 結果

- Tacit Gap Recall
- Unsafe Transfer Prevention
- Clarification Question Coverage

## PyPI公開

```bash
pip install handovergap
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
handovergap audit-sql
```

## 限界

- gold gap annotation is subjective
- handover profile requirements need organization-specific tuning
- LLM-based semantic slot filling can be unstable
- privacy and access control are necessary

## まとめ

- RAGは正しい情報を返しても、引き継ぎ可能とは限らない
- HandoverGap RAGはプロファイルと作業文脈ごとに不足文脈を検出する
- TiDBはスロット、証拠、gapを監査する基盤として使える
