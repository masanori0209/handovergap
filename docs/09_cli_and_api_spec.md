# CLI and API Spec

## CLI Commands

### init

```bash
handovergap init
```

Creates sample files and .env.example.

### demo

```bash
handovergap demo
```

Runs a built-in demo scenario.

### detect

```bash
handovergap detect --scenario S001 --role CS
```

Expected output:

```text
Memory:
A社は今回だけCSVで対応し、APIは次フェーズにする

Detected Gaps:
[HIGH] communication_gap
  顧客にAPI延期を説明済みか不明

[HIGH] authority_gap
  CSが回答してよい範囲が不明

Clarification Questions:
1. 顧客にはAPI延期を説明済みですか？
2. CSが次フェーズ時期を回答してよい範囲はどこまでですか？
```

### evaluate

```bash
handovergap evaluate
```

Expected output:

```text
HandoverGapBench mini

Scenarios: 20
Tacit Gap Recall: 0.76
Unsafe Transfer Prevention: 0.82
Clarification Question Coverage: 0.68
```

### schema

```bash
handovergap schema --dialect tidb
```

Prints TiDB schema.

### serve

```bash
handovergap serve
```

Starts Streamlit demo.

## Python API

```python
from handovergap import HandoverGapDetector, InMemoryStore

store = InMemoryStore.from_builtin_dataset()
detector = HandoverGapDetector(store=store)

result = detector.detect(
    scenario_id="S001",
    successor_role="CS",
)

print(result.gaps)
print(result.questions)
print(result.transferability_score)
```

## Public API Objects

- HandoverGapDetector
- HandoverGapEvaluator
- InMemoryStore
- TiDBStore
- HandoverScenario
- HandoverGapResult
