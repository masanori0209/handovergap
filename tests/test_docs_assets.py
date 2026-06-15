from pathlib import Path


def test_readme_references_comparison_asset() -> None:
    readme = Path("README.md").read_text()
    asset = Path("docs/assets/naive-vs-handovergap.svg")

    assert "docs/assets/naive-vs-handovergap.svg" in readme
    assert asset.exists()
    assert "Naive RAG vs HandoverGap comparison" in asset.read_text()
