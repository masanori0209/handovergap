# Demo Script

## Demo Goal

In 60-90 seconds, show that HandoverGap RAG catches what normal RAG misses.

## Demo Scenario

Memory:

```text
A社は今回だけCSVで対応し、APIは次フェーズにする
```

Successor:

```text
鈴木さん / CS
```

Task:

```text
顧客問い合わせ対応を引き継ぐ
```

## Demo Flow

### 1. Naive RAG

Show:

```text
A社は今回CSV対応です。APIは次フェーズ予定です。
```

Narration:

> 通常のRAGは、正しい情報を検索して回答します。

### 2. Hybrid RAG

Show related evidence.

### 3. HandoverGap RAG

Show gaps:

```text
[HIGH] communication_gap
顧客にAPI延期を説明済みか不明

[HIGH] authority_gap
CSが次フェーズ時期を回答してよい範囲が不明

[MEDIUM] fallback_gap
CSV対応で失敗した場合のエスカレーション先が不明
```

### 4. Clarification Questions

```text
1. 顧客にはAPI延期を説明済みですか？
2. CSが回答してよい次フェーズ時期の範囲はどこまでですか？
3. CSV対応で障害が起きた場合、誰にエスカレーションしますか？
```

### 5. Evaluation

```text
Tacit Gap Recall
naive_rag: 0.18
hybrid_rag: 0.31
handovergap: 0.76
```

## Closing

> 正しい記憶でも、引き継げるとは限らない。
