# Implementation Plan

## P0: Core Package

- [ ] Create pyproject.toml
- [ ] Add Typer CLI
- [ ] Add Pydantic schemas
- [ ] Add built-in HandoverGapBench mini
- [ ] Implement in-memory store
- [ ] Implement rule-based slot filling
- [ ] Implement gap detection
- [ ] Implement question generation templates
- [ ] Implement detect command
- [ ] Implement evaluate command
- [ ] Add tests

## P1: TiDB Integration

- [ ] Add schema.sql
- [ ] Implement TiDBStore
- [ ] Add schema command
- [ ] Add ingest command
- [ ] Persist slot_fill_attempts
- [ ] Persist context_gaps
- [ ] Persist transfer_assessments

## P2: Baselines and Evaluation

- [ ] Implement naive_rag baseline
- [ ] Implement hybrid_rag baseline
- [ ] Add compare option
- [ ] Export evaluation CSV
- [ ] Add article-ready result table

## P3: Demo and Article

- [ ] Add Streamlit demo
- [ ] Add screenshots
- [ ] Add Zenn article draft
- [ ] Add demo video script
- [ ] Add GitHub README polish

## P4: PyPI Release

- [ ] TestPyPI upload
- [ ] PyPI release
- [ ] GitHub Actions CI
- [ ] Trusted Publishing or release workflow
- [ ] Add badges

## MVP Acceptance Criteria

```bash
pip install -e ".[dev]"
handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate
pytest
```
