# HandoverGapBench mini

## Purpose

Evaluate whether a method can detect tacit context gaps in valid-but-non-transferable memories.

## Dataset Unit

Each scenario contains:

- scenario_id
- memory
- evidence_events
- profile
- task_context
- gold_gaps
- gold_questions
- unsafe_transfer_label

## Example

```json
{
  "scenario_id": "S001",
  "memory": "A社は今回だけCSVで対応し、APIは次フェーズにする",
  "evidence_events": [
    {
      "source_type": "slack",
      "content": "じゃあ今回だけCSVで。APIは次フェーズでいいです。"
    },
    {
      "source_type": "issue",
      "content": "API連携は未着手。CSVインポートで暫定対応する。"
    }
  ],
  "profile": "CS",
  "task_context": "顧客問い合わせ対応",
  "gold_gaps": [
    {
      "gap_type": "scope_gap",
      "slot_name": "scope",
      "description": "今回だけが初回リリースのみを指すのか不明"
    },
    {
      "gap_type": "communication_gap",
      "slot_name": "communication_status",
      "description": "顧客にAPI延期を説明済みか不明"
    }
  ],
  "gold_questions": [
    "顧客にはAPI延期を説明済みですか？",
    "CSが次フェーズ時期を回答してよい範囲はどこまでですか？"
  ],
  "unsafe_transfer_label": true
}
```

## MVP Dataset Size

Minimum:

- 20 scenarios
- 3 roles: CS, Engineer, Sales
- 5 gap types

Target for stronger article:

- 50 scenarios
- 3 roles
- 7 gap types
- 3 memory types: decision, procedure, task

## Scenario Categories

- valid but non-transferable
- fully transferable
- stale but transferable after warning
- conflicting and non-transferable
- role-dependent transferability
- missing communication status
- missing fallback path
- missing authority
- missing trigger condition
