# Release Checklist

## Validated Locally

- [x] English PyPI README
- [x] Japanese README
- [x] MIT LICENSE
- [x] CLI entrypoint
- [x] Synthetic benchmark package data
- [x] TiDB schema package data
- [x] Optional dependencies separated
- [x] `ruff check .`
- [x] `pytest`
- [x] `python -m build`
- [x] `twine check dist/*`
- [x] Clean wheel installation and MVP commands

## GitHub Setup Required

- [x] Push repository to `masanori0209/handovergap`
- [x] Confirm default branch name used by README image links
- [x] Add `PYPI_API_TOKEN` repository or environment secret, or configure PyPI Trusted Publisher
- [ ] Add `TEST_PYPI_API_TOKEN` repository or environment secret, or configure TestPyPI Trusted Publisher
- [ ] Enable the `testpypi` GitHub environment
- [ ] Configure TestPyPI Trusted Publisher for `.github/workflows/test-publish.yml`
- [x] Enable the `pypi` GitHub environment with required human approval
- [x] Configure PyPI token publishing for `.github/workflows/publish.yml`
- [x] Confirm CI passes on GitHub

## Publication Approval Required

- [ ] Run the TestPyPI workflow
- [ ] Install from TestPyPI in a clean environment
- [ ] Create and publish a `v0.1.1` GitHub release
- [x] Approve the protected `pypi` environment deployment
- [x] Verify `pip install handovergap`

## Contest Handoff

- [x] Add final GitHub URL to the Zenn article
- [x] Add final PyPI URL to the Zenn article
- [ ] Add hosted demo or video URL if available
- [ ] Publish the Zenn article
