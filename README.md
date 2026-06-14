# HandoverGap RAG

[![CI](https://github.com/masanori0209/handovergap/actions/workflows/ci.yml/badge.svg)](https://github.com/masanori0209/handovergap/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)

[日本語](#日本語) | Repository version: [README.ja.md](https://github.com/masanori0209/handovergap/blob/main/README.ja.md)

HandoverGap RAG detects tacit context that is missing from otherwise correct organizational memories.

> Correct memories are not always transferable.

PyPI: https://pypi.org/project/handovergap/

A normal RAG system may retrieve:

```text
For Company A, use CSV for this release. The API will come in the next phase.
```

The statement can be correct while still being unsafe for a customer-support successor. They may not know:

- whether the customer was informed;
- what “this release” covers;
- what support is authorized to promise;
- what fallback or escalation path to use.

HandoverGap performs role-conditioned slot checks, blocks unsafe transfer, and generates clarification questions.

## Quickstart

```bash
pip install handovergap

handovergap demo
handovergap detect --scenario S001 --role CS
handovergap evaluate --compare
```

No TiDB account, OpenAI key, or external dataset is required.

## Demo

Install the optional Streamlit UI:

```bash
pip install "handovergap[demo]"
handovergap serve
```

The demo defaults to Japanese and includes an English language switch. It compares:

- `naive_rag`: answers directly;
- `hybrid_rag`: adds related evidence;
- `handovergap`: withholds unsafe answers and asks questions.

## Evaluation

`handovergap evaluate --compare` runs the bundled synthetic HandoverGapBench mini dataset.

| Method | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision |
|---|---:|---:|---:|---:|---:|
| naive_rag | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 |
| hybrid_rag | 0.21 | 0.59 | 0.21 | 0.67 | 0.91 |
| handovergap | 1.00 | 0.65 | 1.00 | 1.00 | 1.00 |

These are deterministic results from the bundled 20-scenario dataset. The benchmark is synthetic and intentionally small; it demonstrates reproducible behavior rather than production accuracy.

For a small unknown holdout set with adjudicated synthetic reviewer labels and slot-filling stress profiles:

```bash
handovergap evaluate --dataset holdout --stress-filling
```

| Method | Tacit Gap Recall | Unsafe Transfer Prevention | Question Coverage | Safe Transfer Allowance | Blocked Precision |
|---|---:|---:|---:|---:|---:|
| handovergap/provided | 1.00 | 0.67 | 1.00 | 1.00 | 1.00 |
| handovergap/conservative | 1.00 | 0.67 | 1.00 | 0.67 | 0.67 |
| handovergap/optimistic | 0.64 | 0.67 | 0.64 | 1.00 | 1.00 |

The optimistic profile simulates an LLM over-filling ambiguous slots. It shows a real failure mode: recall drops, while unsafe-transfer prevention stays incomplete at `0.67`.

With optional live OpenAI semantic slot filling:

```bash
python harness/validation/openai_slot_filling_check.py --dataset holdout --persist-tidb
```

Observed with `gpt-4.1-mini`: tacit gap recall `0.91`, unsafe transfer prevention `0.33`, safe transfer allowance `0.67`, blocked precision `0.50`. The detailed per-scenario output is saved to `article/openai_slot_filling_results.json`.

![Japanese Streamlit demo](https://raw.githubusercontent.com/masanori0209/handovergap/main/docs/assets/demo-ja.png)

## Optional TiDB Store

```bash
pip install "handovergap[tidb]"
handovergap schema --dialect tidb
```

```python
from handovergap import TiDBStore

store = TiDBStore("mysql+pymysql://user:password@host:4000/handovergap")
store.create_schema()
```

The packaged schema models source evidence, memories, role requirements, slot-fill attempts, context gaps, clarification questions, transfer assessments, and evaluation runs. Live persistence methods are available for slot-fill attempts, context gaps, transfer assessments, and evaluation runs.

### Live TiDB Validation

After creating a TiDB Cloud cluster, open **Connect**, choose a public Python/SQLAlchemy-compatible connection, generate or reset the password, and export the connection values locally:

```bash
export TIDB_HOST="..."
export TIDB_PORT="4000"
export TIDB_USER="..."
export TIDB_PASSWORD="..."
export TIDB_DB_NAME="test"
export TIDB_CA_PATH="/path/to/ca-certificates.crt"
```

Then run:

```bash
python harness/validation/tidb_live_check.py --create-schema
```

The check creates the packaged schema if needed, writes one synthetic memory, persists a slot-fill attempt, a context gap, a transfer assessment, and the holdout stress evaluation runs, then prints row counts as JSON. Do not commit `.env` files or TiDB credentials.

## Python API

```python
from handovergap import HandoverGapDetector, InMemoryStore

store = InMemoryStore.from_builtin_dataset()
detector = HandoverGapDetector(store)
result = detector.detect(scenario_id="S001", successor_role="CS")

print(result.transferability_status)
print(result.gaps)
print(result.questions)
```

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev,demo]"
.venv/bin/pytest
```

## Limitations

- The bundled detector and baselines are deterministic rules, not learned models.
- HandoverGapBench mini and holdout contain synthetic scenarios.
- Slot-filling stress profiles simulate LLM variance; they are not a replacement for a live LLM evaluation.
- Live OpenAI slot filling is optional and not required for first-run usage.
- Semantic equivalence scoring for generated questions is not implemented in the MVP.
- Live TiDB integration requires the optional `tidb` extra and a configured database.

## License

MIT

## 日本語

HandoverGap RAGは、正しい業務記憶に不足している暗黙前提を、引き継ぎ先の役割ごとに検出します。

> 正しい記憶でも、引き継げるとは限らない。

```bash
pip install handovergap
handovergap demo
handovergap detect --scenario S001 --role CS
handovergap evaluate --compare
```

Streamlitデモは日本語がデフォルトで、英語へ切り替えられます。

```bash
pip install "handovergap[demo]"
handovergap serve
```

詳細な日本語ドキュメントは[README.ja.md](https://github.com/masanori0209/handovergap/blob/main/README.ja.md)を参照してください。
