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

- [ ] Push repository to `masanori0209/handovergap`
- [ ] Confirm default branch name used by README image links
- [ ] Enable the `testpypi` GitHub environment
- [ ] Configure TestPyPI Trusted Publisher for `.github/workflows/test-publish.yml`
- [ ] Enable the `pypi` GitHub environment with required human approval
- [ ] Configure PyPI Trusted Publisher for `.github/workflows/publish.yml`
- [ ] Confirm CI passes on GitHub

## Publication Approval Required

- [ ] Run the TestPyPI workflow
- [ ] Install from TestPyPI in a clean environment
- [ ] Create and publish a `v0.1.0` GitHub release
- [ ] Approve the protected `pypi` environment deployment
- [ ] Verify `pip install handovergap`

## Contest Handoff

- [ ] Add final GitHub URL to the Zenn article
- [ ] Add final PyPI URL to the Zenn article
- [ ] Add hosted demo or video URL if available
- [ ] Publish the Zenn article
