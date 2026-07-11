#!/usr/bin/env python3
"""Validate a public CEAPP source directory with no third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


TEXT_SUFFIXES = {".html", ".css", ".js", ".mjs", ".json", ".md", ".txt", ".py", ".sh"}
APP_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-_.]{1,63}$")
REMOTE_HTML_PATTERN = re.compile(r"(?:src|href)\s*=\s*[\"']https?://", re.IGNORECASE)
REMOTE_CSS_PATTERN = re.compile(r"(?:@import\s+|url\s*\()[\"']?https?://", re.IGNORECASE)
REMOTE_JS_PATTERN = re.compile(r"(?:from\s+|import\s*\()[\"']https?://", re.IGNORECASE)
PRIVATE_PATTERNS = {
    "private key": re.compile(r"BEGIN(?: [A-Z]+)? PRIVATE KEY", re.IGNORECASE),
    "credential assignment": re.compile(
        r"\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*[\"'][^\"']{8,}[\"']",
        re.IGNORECASE,
    ),
    "macOS user path": re.compile(r"/Users/[^/\s]+/"),
    "Linux user path": re.compile(r"/home/[^/\s]+/"),
    "Windows user path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\"),
    "private IPv4 address": re.compile(
        r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
    ),
    "local debug endpoint": re.compile(r"https?://(?:localhost|127\.0\.0\.1)(?::\d+)?", re.IGNORECASE),
}


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.warnings: list[str] = []
        self.passes: list[str] = []

    def require(self, condition: bool, success: str, failure: str) -> None:
        if condition:
            self.passes.append(success)
        else:
            self.failures.append(failure)

    def warn(self, condition: bool, message: str) -> None:
        if condition:
            self.warnings.append(message)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def package_path(root: Path, value: object) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    return root / candidate


def locale_message_keys(js_text: str, locale: str) -> set[str]:
    start_match = re.search(rf"^\s{{2}}[\"']{re.escape(locale)}[\"']\s*:\s*\{{", js_text, re.MULTILINE)
    if not start_match:
        return set()
    remainder = js_text[start_match.end() :]
    next_locale = re.search(r"^\s{2}[\"'](?:zh-CN|en-US)[\"']\s*:\s*\{", remainder, re.MULTILINE)
    messages_end = re.search(r"^\s{2}\}\s*\n\}", remainder, re.MULTILINE)
    end_candidates = [match.start() for match in (next_locale, messages_end) if match]
    end_offset = min(end_candidates) if end_candidates else len(remainder)
    block = js_text[start_match.end() : start_match.end() + end_offset]
    return set(re.findall(r"^\s{4}[\"']([^\"']+)[\"']\s*:", block, re.MULTILINE))


def validate_manifest(root: Path, manifest: dict, report: Report) -> None:
    app_id = str(manifest.get("appId", "")).strip()
    report.require(manifest.get("schemaVersion") == 1, "schemaVersion is 1", "app.json schemaVersion must be 1")
    report.require(bool(APP_ID_PATTERN.fullmatch(app_id)), "appId format is valid", "appId must be 2-64 lowercase letters, digits, dots, underscores, or hyphens")
    report.require(bool(str(manifest.get("name", "")).strip()), "name is present", "app.json requires name")
    report.require(bool(str(manifest.get("version", "")).strip()), "version is present", "app.json requires an app-owned version")

    entry = package_path(root, manifest.get("entry"))
    report.require(entry is not None and entry.is_file(), "entry exists", "entry must be a package-relative file that exists")
    icon = package_path(root, manifest.get("icon"))
    report.require(icon is not None and icon.is_file(), "icon exists", "icon must be a package-relative file that exists")

    commands = manifest.get("commands")
    report.require(isinstance(commands, dict) and bool(commands), "commands is non-empty", "current CanEngine validation requires at least one command")
    if isinstance(commands, dict):
        for command_id, command in commands.items():
            report.require(bool(str(command_id).strip()), f"command id {command_id!r} is valid", "command ids cannot be empty")
            report.require(isinstance(command, dict) and bool(str(command.get("executable", "")).strip()), f"command {command_id} has an executable", f"command {command_id} requires executable")

    permissions = manifest.get("permissions", [])
    report.require(isinstance(permissions, list), "permissions is an array", "permissions must be an array of strings")
    permission_set = {str(item).strip() for item in permissions if str(item).strip()} if isinstance(permissions, list) else set()
    report.warn(len(permission_set) > 10, f"{len(permission_set)} permissions are declared; review whether every one is necessary")

    capabilities = manifest.get("capabilities") or {}
    ai = capabilities.get("ai") or {}
    for feature in ai.get("features") or []:
        report.require(feature in permission_set, f"AI feature {feature} has matching permission", f"AI feature {feature} must also appear in permissions")

    notification = capabilities.get("notification") or {}
    for capability in notification.get("capabilities") or []:
        permission = f"notification.{capability}"
        report.require(permission in permission_set, f"notification capability {capability} has matching permission", f"notification capability {capability} requires {permission}")

    data_bridge = capabilities.get("dataBridge") or {}
    mode = str(data_bridge.get("mode", "")).strip()
    mode_permission = {"read": "data.read", "write": "data.write", "export": "data.export"}.get(mode)
    if mode_permission:
        report.require(mode_permission in permission_set, f"Data Bridge mode {mode} has matching permission", f"Data Bridge mode {mode} requires {mode_permission}")
    if data_bridge.get("actions"):
        report.require("data.action" in permission_set, "Data Bridge actions have matching permission", "Data Bridge actions require data.action")
    if data_bridge.get("local"):
        report.require(bool({"data.read", "data.write"} & permission_set), "local Data Bridge has read/write permission", "local Data Bridge requires data.read or data.write")
        schema_entry = package_path(root, (data_bridge.get("local") or {}).get("schemaEntry"))
        if (data_bridge.get("local") or {}).get("schemaEntry"):
            report.require(schema_entry is not None and schema_entry.is_file(), "local Data Bridge schema exists", "dataBridge.local.schemaEntry must exist inside the project")

    manifest_app_id = app_id
    app_js = read_text(root / "app.js")
    if app_js:
        id_match = re.search(r"\bAPP_ID\s*=\s*[\"']([^\"']+)[\"']", app_js)
        report.require(not id_match or id_match.group(1) == manifest_app_id, "app.json and JavaScript appId match", "APP_ID in app.js must match app.json appId")


def validate_sources(root: Path, report: Report) -> None:
    symlinks = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_symlink()]
    report.require(not symlinks, "project contains no symlinks", f"remove symlinks from the public package root: {', '.join(symlinks)}")

    blocked_names = {".env", ".DS_Store", "Thumbs.db"}
    blocked_suffixes = {".ceapp", ".pem", ".key", ".p12", ".pfx"}
    blocked_files = [
        str(path.relative_to(root))
        for path in root.rglob("*")
        if path.is_file() and (path.name in blocked_names or path.suffix.lower() in blocked_suffixes)
    ]
    report.require(not blocked_files, "project root has no secret/build artifacts", f"remove non-runtime or sensitive files: {', '.join(blocked_files)}")
    archive_suffixes = {".dmg", ".zip", ".tar", ".gz"}
    archive_files = [str(path.relative_to(root)) for path in root.rglob("*") if path.is_file() and path.suffix.lower() in archive_suffixes]
    report.warn(bool(archive_files), f"review whether packaged archives are required at runtime: {', '.join(archive_files)}")

    text_files = [path for path in root.rglob("*") if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and not any(part in {"node_modules", ".git", "dist"} for part in path.parts)]
    combined = "\n".join(read_text(path) for path in text_files)

    index_text = read_text(root / "index.html")
    css_text = "\n".join(read_text(path) for path in text_files if path.suffix.lower() == ".css")
    js_text = "\n".join(read_text(path) for path in text_files if path.suffix.lower() in {".js", ".mjs"})
    report.require(not REMOTE_HTML_PATTERN.search(index_text), "HTML has no remote startup assets", "index.html must not load remote src/href assets")
    report.require(not REMOTE_CSS_PATTERN.search(css_text), "CSS has no remote imports", "CSS must not import remote assets for the local shell")
    report.require(not REMOTE_JS_PATTERN.search(js_text), "JavaScript has no remote imports", "JavaScript must not import remote modules at runtime")
    report.require("'zh-CN'" in js_text or '"zh-CN"' in js_text, "zh-CN messages are present", "runtime code must include zh-CN messages")
    report.require("'en-US'" in js_text or '"en-US"' in js_text, "en-US messages are present", "runtime code must include en-US messages")

    zh_keys = locale_message_keys(js_text, "zh-CN")
    en_keys = locale_message_keys(js_text, "en-US")
    if zh_keys and en_keys:
        only_zh = sorted(zh_keys - en_keys)
        only_en = sorted(en_keys - zh_keys)
        mismatch = [f"missing from en-US: {', '.join(only_zh)}" if only_zh else "", f"missing from zh-CN: {', '.join(only_en)}" if only_en else ""]
        report.require(not only_zh and not only_en, "zh-CN and en-US message keys match", "; ".join(item for item in mismatch if item))

    html_i18n_keys = set(re.findall(r"data-i18n(?:-placeholder|-alt)?=[\"']([^\"']+)[\"']", index_text))
    missing_keys = sorted(key for key in html_i18n_keys if key not in js_text)
    report.require(not missing_keys, "HTML i18n keys are represented in JavaScript", f"missing message keys referenced by HTML: {', '.join(missing_keys)}")

    for label, pattern in PRIVATE_PATTERNS.items():
        matches = []
        for path in text_files:
            if path.name == "LICENSE":
                continue
            if pattern.search(read_text(path)):
                matches.append(str(path.relative_to(root)))
        report.require(not matches, f"no {label} found", f"public-source scan found {label} in: {', '.join(matches)}")

    report.warn("cdn.tailwindcss.com" in combined, "cdn.tailwindcss.com is present and must be removed")
    report.warn("fonts.googleapis.com" in combined, "a remote Google Fonts reference is present and must be removed")


def print_report(root: Path, report: Report) -> int:
    print(f"CEAPP validation: {root}")
    for item in report.passes:
        print(f"  PASS  {item}")
    for item in report.warnings:
        print(f"  WARN  {item}")
    for item in report.failures:
        print(f"  FAIL  {item}")
    print(f"Summary: {len(report.passes)} passed, {len(report.warnings)} warnings, {len(report.failures)} failed")
    return 1 if report.failures else 0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_ceapp.py /path/to/ceapp-project", file=sys.stderr)
        return 2
    root = Path(sys.argv[1]).expanduser().resolve()
    report = Report()
    report.require(root.is_dir(), "project directory exists", f"project directory does not exist: {root}")
    manifest_path = root / "app.json"
    report.require(manifest_path.is_file(), "app.json exists", "project root requires app.json")
    report.require((root / "index.html").is_file(), "index.html exists", "project root requires index.html")
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            report.passes.append("app.json is valid JSON")
            validate_manifest(root, manifest, report)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
            report.failures.append(f"app.json is not valid UTF-8 JSON: {error}")
    if root.is_dir():
        validate_sources(root, report)
    return print_report(root, report)


if __name__ == "__main__":
    raise SystemExit(main())
