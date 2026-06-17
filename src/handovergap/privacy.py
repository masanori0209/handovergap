from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

DEFAULT_PRIVACY_CHECK_PATHS = [
    "README.md",
    "README.ja.md",
    "SECURITY.md",
    "docs",
    "examples",
    "src/handovergap/data",
    "article/independent_gap_label_review.md",
    "article/independent_gap_label_review.json",
]

SECRET_PATTERNS = [
    ("openai_api_key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    (
        "assigned_secret",
        re.compile(
            r"(?i)\b(?:OPENAI_API_KEY|TIDB_PASSWORD|TIDB_PRIVATE_KEY|PYPI_API_TOKEN|GITHUB_TOKEN)\s*=\s*[\"']?([^\"'\s]+)"
        ),
    ),
    ("slack_user_mention", re.compile(r"<@U[A-Z0-9]{6,}>")),
    ("email_address", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)),
]

SAFE_PLACEHOLDERS = {"...", "example", "example.com", "dummy", "placeholder", "redacted", "test"}
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "build", "dist", "reports"}
TEXT_SUFFIXES = {".md", ".txt", ".json", ".jsonl", ".csv", ".html", ".yml", ".yaml", ".py", ".sh"}


@dataclass(frozen=True)
class PrivacyFinding:
    path: str
    line: int
    kind: str
    excerpt: str


def scan_privacy(paths: list[str] | None = None) -> list[PrivacyFinding]:
    roots = [Path(path) for path in (paths or DEFAULT_PRIVACY_CHECK_PATHS)]
    findings: list[PrivacyFinding] = []
    for file_path in _iter_files(roots):
        findings.extend(_scan_file(file_path))
    return findings


def _iter_files(roots: list[Path]):
    for root in roots:
        if not root.exists():
            continue
        if root.is_file():
            if _should_scan(root):
                yield root
            continue
        for path in root.rglob("*"):
            if path.is_file() and _should_scan(path):
                yield path


def _should_scan(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    return path.suffix.lower() in TEXT_SUFFIXES


def _scan_file(path: Path) -> list[PrivacyFinding]:
    findings = []
    try:
        lines = path.read_text(errors="ignore").splitlines()
    except OSError:
        return findings
    for line_number, line in enumerate(lines, start=1):
        for kind, pattern in SECRET_PATTERNS:
            for match in pattern.finditer(line):
                if _is_safe_match(kind, match):
                    continue
                findings.append(
                    PrivacyFinding(
                        path=str(path),
                        line=line_number,
                        kind=kind,
                        excerpt=_redacted_excerpt(line),
                    )
                )
    return findings


def _is_safe_match(kind: str, match: re.Match[str]) -> bool:
    if kind == "assigned_secret":
        value = match.group(1).strip().strip("\"'")
        normalized = value.lower()
        return normalized in SAFE_PLACEHOLDERS or normalized.startswith("your_") or normalized.startswith("<")
    if kind == "email_address":
        return match.group(0).lower().endswith("@example.com")
    return False


def _redacted_excerpt(line: str) -> str:
    excerpt = line.strip()
    excerpt = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "sk-...REDACTED", excerpt)
    excerpt = re.sub(
        r"(?i)(OPENAI_API_KEY|TIDB_PASSWORD|TIDB_PRIVATE_KEY|PYPI_API_TOKEN|GITHUB_TOKEN)\s*=\s*[\"']?([^\"'\s]+)",
        r"\1=...REDACTED",
        excerpt,
    )
    if len(excerpt) > 140:
        return excerpt[:137] + "..."
    return excerpt
