#!/usr/bin/env bash
set -euo pipefail

pytest
ruff check .
python -m build
twine check dist/*
