# Loop 09: Article Loop

## Objective

Update article draft with implementation-backed claims.

## Input Files

- `article/zenn_outline.md`
- `article/key_phrases.md`
- evaluation output
- screenshots if available

## Output Files

- `article/zenn_draft.md`
- `article/results.md`

## Forbidden Changes

- Do not overclaim novelty.
- Do not cite unsupported benchmark results.
- Do not hide limitations.

## Validation Commands

```bash
handovergap evaluate --compare
```

## Stop Condition

Article draft includes results table, CLI quickstart, TiDB schema, and limitations.
