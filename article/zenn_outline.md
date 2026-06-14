# Zenn Article Outline

# 正しい記憶でも、引き継げるとは限らない：TiDBで作る HandoverGap RAG

## はじめに

- RAGは正しい情報を返せる
- でも業務引き継ぎでは、それだけでは足りない
- 正しいが引き継げない記憶がある

## 例: 「今回だけCSV」

- Naive RAGはそのまま答える
- でもCSが引き継ぐには情報が足りない

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
- successor role requirements
- slot filling
- evidence retrieval
- gap detection
- clarification questions

## TiDBを使う理由

- Vector Storeではなくslot/evidence/gap store
- SQL + Vector + Full-text + JSON + Transaction
- slot filling processを保存できる

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
handovergap detect --sample S001 --role CS
handovergap evaluate
```

## 限界

- gold gap annotation is subjective
- role requirements need domain tuning
- LLM-based slot filling can be unstable
- privacy and access control are necessary

## まとめ

- RAGは正しい情報を返しても、引き継ぎ可能とは限らない
- HandoverGap RAGは受け手ごとに不足文脈を検出する
- TiDBはslot/evidence/gapを管理する基盤として使える
