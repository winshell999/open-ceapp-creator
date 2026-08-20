#!/usr/bin/env python3
"""Audit this public repository for common secret and environment leaks."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", "release"}
TEXT_SUFFIXES = {
    "", ".md", ".txt", ".json", ".yaml", ".yml", ".html", ".css", ".js", ".mjs",
    ".py", ".sh", ".toml", ".ini", ".cfg", ".xml",
}
BLOCKED_NAMES = {".DS_Store", "Thumbs.db", ".env"}
BLOCKED_SUFFIXES = {".pem", ".key", ".p12", ".pfx", ".ceapp"}
SCANNER_FILES = {Path("scripts/audit_public_repo.py"), Path("scripts/validate_ceapp.py")}

PATTERNS: dict[str, re.Pattern[str]] = {
    "private key material": re.compile(r"-----BEGIN(?: [A-Z0-9]+)? PRIVATE KEY-----", re.IGNORECASE),
    "GitHub token": re.compile(r"\b(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})\b"),
    "credential assignment": re.compile(
        r"\b(?:api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|passwd)"
        r"\s*[:=]\s*[\"'][^\"'\n]{8,}[\"']",
        re.IGNORECASE,
    ),
    "credentialed URL": re.compile(r"https?://[^\s/@:]+:[^\s/@]+@[^\s/]+", re.IGNORECASE),
    "macOS user path": re.compile(r"/Users/[^/\s<>]+/"),
    "Linux user path": re.compile(r"/home/[^/\s<>]+/"),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s<>]+\\"),
    "private IPv4 address": re.compile(
        r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|"
        r"172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
    ),
    "localhost URL": re.compile(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?(?:/[^\s]*)?", re.IGNORECASE),
}

# The scanners intentionally contain regex examples for path/network detection.
SCANNER_PATTERN_EXEMPTIONS = {
    "macOS user path",
    "Linux user path",
    "Windows user path",
    "private IPv4 address",
    "localhost URL",
}


def iter_files() -> list[Path]:
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return files


def read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", ".gitignore"}:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def audit_remote(issues: list[str]) -> None:
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return

    if result.returncode != 0:
        return

    remote = result.stdout.strip()
    if not remote:
        return

    if remote.startswith(("http://", "https://")):
        parsed = urlsplit(remote)
        if parsed.username is not None or parsed.password is not None or "@" in parsed.netloc:
            issues.append("Git origin embeds credentials/user-info; use a credential-free remote URL")


def main() -> int:
    issues: list[str] = []
    warnings: list[str] = []

    for path in iter_files():
        relative = path.relative_to(ROOT)

        if path.name in BLOCKED_NAMES or path.suffix.lower() in BLOCKED_SUFFIXES:
            issues.append(f"blocked public-repo artifact: {relative}")

        if path.name.startswith(".env.") and path.name != ".env.example":
            issues.append(f"environment file must not be committed: {relative}")

        text = read_text(path)
        if text is None:
            continue

        for label, pattern in PATTERNS.items():
            if relative in SCANNER_FILES and label in SCANNER_PATTERN_EXEMPTIONS:
                continue
            if pattern.search(text):
                issues.append(f"{label}: {relative}")

        if "window.runtime." in text and relative.suffix.lower() in {".js", ".html"}:
            warnings.append(f"CEAPP runtime code references window.runtime directly: {relative}")

    audit_remote(issues)

    print(f"Public repository audit: {ROOT}")
    for warning in sorted(set(warnings)):
        print(f"  WARN  {warning}")
    for issue in sorted(set(issues)):
        print(f"  FAIL  {issue}")

    if issues:
        print(f"Summary: {len(set(issues))} failure(s), {len(set(warnings))} warning(s)")
        return 1

    print("  PASS  no common secret/path/private-network leaks detected")
    print(f"Summary: 0 failures, {len(set(warnings))} warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
