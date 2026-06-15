# PyPI Package Design

## Package Name

Preferred:

```text
handovergap
```

Alternatives:

- handover-gap-rag
- tacitgap
- tacit-context-gap

## Package Goal

Enable users to run:

```bash
pip install handovergap
handovergap detect --scenario S001 --profile CS
handovergap evaluate --compare
handovergap serve
```

## pyproject.toml Draft

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "handovergap"
version = "0.1.0"
description = "Tacit Context Gap Detection for Handover-oriented RAG"
readme = "README.md"
requires-python = ">=3.10"
license = "MIT"
authors = [
  { name = "Masa Mura" }
]
keywords = ["rag", "llm", "tidb", "handover", "agent-memory"]
classifiers = [
  "Development Status :: 3 - Alpha",
  "Intended Audience :: Developers",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
]

dependencies = [
  "typer>=0.12",
  "pydantic>=2",
  "rich>=13",
]

[project.optional-dependencies]
openai = ["openai>=1"]
demo = ["streamlit>=1.30"]
tidb = ["sqlalchemy>=2", "pymysql>=1", "python-dotenv>=1"]
live = ["streamlit>=1.30", "openai>=1", "sqlalchemy>=2", "pymysql>=1", "python-dotenv>=1"]
dev = ["pytest>=8", "ruff>=0.5", "mypy>=1", "build>=1", "twine>=5"]

[project.scripts]
handovergap = "handovergap.cli:app"
```

## Release Levels

### 0.1.0

- CLI
- in-memory store
- sample benchmark
- detect
- evaluate

### 0.2.0

- TiDB store
- schema command
- audit-sql command
- ingest command
- Streamlit demo

### 0.3.0

- optional OpenAI slot filling
- richer benchmark
- exported evaluation reports

## PyPI Readiness Checklist

- README quickstart
- LICENSE
- pyproject.toml
- package metadata
- tests
- GitHub Actions CI
- TestPyPI check
- PyPI trusted publishing or twine upload
