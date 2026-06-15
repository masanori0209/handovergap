# 正しい記憶でも、引き継げるとは限らない：TiDBで作る HandoverGap RAG

## はじめに

Slackにこう残っていました。

```text
A社は今回だけCSVで対応し、APIは次フェーズで。
```

RAGはこの記憶を正しく検索できます。  
でも、翌週から顧客対応を引き継ぐ人は、この一文だけで対応できるでしょうか？

足りないものがあります。

- 「今回だけ」の範囲
- 顧客に説明済みか
- 顧客向けに回答してよい範囲
- 失敗時のエスカレーション先
- 次フェーズの条件

この記事では、このような **正しいが引き継げない記憶** を検出する HandoverGap RAG を実装します。

## 問題設定

通常のRAGは、関連する情報を検索して回答します。

しかし、業務引き継ぎではそれだけでは足りません。

```text
Correctness != Transferability
```

## valid-but-non-transferable memory

...

## HandoverGap RAGのアプローチ

...

## TiDBをどう使ったか

...

## PyPIで試す

```bash
pip install handovergap
handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
```

## HandoverGapBench mini

...

## 比較実験

...

## 実装して分かったこと

...

## 限界

...

## まとめ

正しい記憶でも、引き継げるとは限りません。

HandoverGap RAGは、RAGが答える前に「この記憶は本当に受け手が安全に使えるのか」を検査するための基盤です。
