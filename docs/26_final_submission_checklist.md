# Final Submission Checklist

## Repository

- [x] Repository name: handovergap
- [x] Description set
- [x] README polished
- [x] LICENSE present
- [x] pyproject.toml present
- [x] tests present
- [x] GitHub Actions passing
- [x] sample dataset included
- [x] schema.sql included
- [x] examples included
- [x] live TiDB Developer Tier validation completed
- [x] holdout dataset with adjudicated synthetic reviewer labels included
- [x] slot filling stress evaluation included
- [x] optional live OpenAI slot filling validation completed

## GitHub Description

```text
Detect tacit context gaps in handover-oriented RAG — because correct memories are not always transferable.
```

## Package

- [ ] PyPI package published or TestPyPI if time-constrained
- [ ] `pip install handovergap` works
- [x] local wheel installation works
- [x] `handovergap demo` works
- [x] `handovergap evaluate` works
- [x] package data included

## CLI

- [x] `handovergap --help`
- [x] `handovergap demo`
- [x] `handovergap detect --scenario S001 --role CS`
- [x] `handovergap evaluate`
- [x] `handovergap evaluate --compare`
- [x] `handovergap evaluate --dataset holdout --stress-filling`
- [x] `handovergap schema --dialect tidb`
- [x] `python harness/validation/tidb_live_check.py --create-schema`
- [x] `python harness/validation/openai_slot_filling_check.py --dataset holdout --persist-tidb`

## Evaluation

- [x] HandoverGapBench mini has 20+ scenarios
- [x] at least 3 roles
- [x] at least 5 gap types
- [x] baselines included
- [x] metrics documented
- [x] safe-transfer and blocked-precision metrics documented
- [x] live TiDB evaluation_runs persistence validated
- [x] live OpenAI slot filling metrics documented

## Article

- [x] strong opening example
- [x] concept definition
- [x] method diagram
- [x] TiDB schema
- [x] package quickstart
- [x] evaluation table
- [x] competitor positioning
- [x] limitations
- [x] link to GitHub
- [ ] link to PyPI
- [ ] link to demo/video if available

## Final Article Title

```text
正しい記憶でも、引き継げるとは限らない：TiDBで作る HandoverGap RAG
```

Subtitle:

```text
受け手ごとに不足する暗黙前提を検出する、PyPI公開つきRAG評価基盤
```
