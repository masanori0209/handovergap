from pathlib import Path


def test_readme_references_comparison_asset() -> None:
    readme = Path("README.md").read_text()
    asset = Path("docs/assets/naive-vs-handovergap.svg")

    assert "docs/assets/naive-vs-handovergap.svg" in readme
    assert asset.exists()
    assert "Naive RAG vs HandoverGap comparison" in asset.read_text()


def test_github_pages_has_task_oriented_library_sections() -> None:
    page = Path("docs/index.html").read_text()

    expected_sections = [
        'id="documentation-map"',
        'id="quickstart"',
        'id="concepts"',
        'id="cli-reference"',
        'id="python-api"',
        'id="profile-yaml-reference"',
        'id="rag-integration"',
        'id="tidb-audit-store"',
        'id="evaluation-guide"',
        'id="security-privacy"',
    ]

    for section in expected_sections:
        assert section in page

    assert "Documentation Map" in page
    assert "Profile YAML Reference" in page
    assert "Security And Privacy" in page


def test_github_pages_avoids_production_accuracy_claims() -> None:
    page = Path("docs/index.html").read_text()

    assert "not production accuracy" in page
    assert "not a general accuracy guarantee" in page
    assert "your own anonymized local data" in page
