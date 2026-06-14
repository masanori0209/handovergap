# CODEX.md

## Mission

Implement `handovergap`, a Python package and CLI for detecting tacit context gaps in handover-oriented RAG.

## Priority Order

1. CLI first-run experience
2. evaluation reproducibility
3. baseline comparison
4. TiDB-specific implementation
5. article assets
6. demo polish

## Core Commands

```bash
handovergap demo
handovergap detect --scenario S001 --role CS
handovergap evaluate --compare
handovergap schema --dialect tidb
```

## Constraints

- Python >= 3.10
- Typer CLI
- Pydantic v2
- Rich output
- pytest
- no required external LLM in P0
- no required TiDB in local MVP
- synthetic data only

## Stop Rule

Do not move to the next loop automatically.  
End with a loop report.
