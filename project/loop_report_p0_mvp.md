# Loop Report

## Objective

Implement the P0 package, schema, dataset, detect CLI, and evaluate CLI loops as a reproducible first-run artifact.

## Winning Gate

This improves PyPI first-run experience, evaluation evidence, article comparison metrics, demo clarity, and TiDB relevance through an optional schema command.

## Files Changed

- `pyproject.toml`
- `src/handovergap/`
- `tests/`
- `README.md`
- `.gitignore`

## Validation

- [x] `.venv/bin/handovergap --help`
- [x] `.venv/bin/handovergap demo`
- [x] `.venv/bin/handovergap detect --scenario S001 --profile CS`
- [x] `.venv/bin/handovergap evaluate --compare`
- [x] `.venv/bin/pytest`

## Observations

- HandoverGapBench mini contains 20 synthetic scenarios across CS, Engineer, and Sales.
- The deterministic detector uses profile-conditioned missing slots, so P0 does not require OpenAI or TiDB.
- `hybrid_rag` is intentionally weak but non-zero, giving the article a more credible comparison than a naive-only baseline.

## Failures

- System `python3 -m pip install -e ".[dev]"` was blocked by PEP 668, so validation used a local `.venv`.
- Initial Rich table output wrapped at narrow terminal width; CLI console width was adjusted for demo readability.

## Context Updates

- Use `.venv/bin/...` commands locally unless the environment has an activated virtualenv.
- P1 should improve comparison methodology before adding broad features.

## Next Recommended Loop

Loop 06: baseline comparison, focusing on article-ready methodology and limitations.
