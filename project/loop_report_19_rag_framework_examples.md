# Loop Report

## Objective

Add dependency-free LangChain and LlamaIndex examples showing where to place `TransferabilityGate` before final answer generation.

## Files Changed

- `examples/langchain_gate.py`
- `examples/llamaindex_gate.py`
- `README.md`
- `tests/test_examples.py`

## Validation

- [x] `.venv/bin/pytest`
- [x] `.venv/bin/ruff check .`
- [x] `.venv/bin/python examples/langchain_gate.py`
- [x] `.venv/bin/python examples/llamaindex_gate.py`

## Evaluation Integrity

- [x] examples do not read gold labels
- [x] examples do not add OpenAI/TiDB/runtime dependencies
- [x] examples show gate-before-answer behavior, not benchmark optimization

## Observations

- The examples are intentionally plain Python so users can map their own LangChain/LlamaIndex retriever outputs into `TransferabilityGate.check(...)`.
- This reinforces HandoverGap as an answer gate, not a replacement vector store.

## Failures

- None.

## Next Recommended Loop

Issue #10: add README comparison visual or generated comparison artifact.
