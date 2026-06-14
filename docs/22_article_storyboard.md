# Article Storyboard

## Reader Emotion Design

1. Recognition: "This handover problem happens."
2. Surprise: "Correct RAG output can still be dangerous."
3. Clarity: "Transferability is different from correctness."
4. Trust: "The method is schema-driven and evaluated."
5. Action: "I can run this package."

## Opening Scene

```text
Slackにこう残っていました。

「A社は今回だけCSVで対応し、APIは次フェーズで」

RAGはこの情報を正しく検索できます。
でも、翌週からCS担当になった人は、この一文だけで顧客対応できるでしょうか？
```

## Main Contrast

| System | Behavior |
|---|---|
| Naive RAG | 検索結果をもとに回答する |
| Hybrid RAG | 関連ログも添えて回答する |
| HandoverGap RAG | 不足する暗黙前提を検出し、確認質問を出す |

## Key Diagram

```text
Memory
  + Successor Role
  + Handover Task
  + Evidence
      ↓
Role-conditioned Slot Filling
      ↓
Tacit Context Gaps
      ↓
Clarification Questions
      ↓
Transferability Assessment
```

## Avoid

Do not start with TiDB schema.

Do not start with PyPI.

Do not start with "I built a RAG app."

Start with the failure mode.
