# Judging Scorecard

Use this scorecard before publishing.

| Category | Weight | Required Evidence |
|---|---:|---|
| Theme Fit | 15 | RAG / agent memory framing |
| TiDB Fit | 15 | schema + SQL/vector/full-text/JSON use |
| Originality | 15 | valid-but-non-transferable memory |
| Implementation Depth | 15 | GitHub + package + tests |
| Reproducibility | 10 | pip install + quickstart |
| Evaluation | 10 | HandoverGapBench mini |
| Engineering Usefulness | 10 | pitfalls + reusable patterns |
| Article Quality | 5 | clear story + diagrams |
| Demo Impact | 5 | comparison demo |

Target: 88+.

## Publish Gate

Do not publish until all of these pass:

```bash
pip install -e ".[dev]"
handovergap demo
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
pytest
```

And the article contains:

- one clear example
- one architecture diagram
- one schema excerpt
- one metric table
- one screenshot
- one limitations section
