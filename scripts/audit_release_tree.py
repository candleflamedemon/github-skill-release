#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


TEXT_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".css",
    ".csv",
    ".gitattributes",
    ".gitignore",
    ".html",
    ".js",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".rst",
    ".sh",
    ".toml",
    ".ts",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

SECRET_PATTERNS = [
    (r"\b(api[_-]?key|secret|password|passwd|access[_-]?token|refresh[_-]?token|private[_-]?key|client[_-]?secret|authorization|bearer)\b\s*[:=]\s*['\"]?[^'\"\s]{8,}", "assigned-secret-like-value"),
    (r"\bsk-[A-Za-z0-9]{20,}\b", "openai-like-token"),
    (r"\bgithub_pat_[A-Za-z0-9_]{20,}\b", "github-pat"),
    (r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b", "github-token"),
    (r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b", "slack-token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "aws-access-key"),
]

PRIVACY_PATTERNS = [
    (r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "email"),
    (r"\b1[3-9]\d{9}\b", "cn-phone-like"),
    (r"\b\d{3}[- .]?\d{3}[- .]?\d{4}\b", "us-phone-like"),
    (r"\b\d{15}(\d{2}[0-9Xx])?\b", "cn-id-like"),
    (r"姓名|身份证|手机号|电话|地址|住址|邮箱|微信|QQ", "privacy-keyword"),
]

LOCAL_PATH_PATTERNS = [
    (r"[A-Za-z]:\\", "windows-path"),
    (r"\b[A-Za-z]:/", "windows-path"),
    (r"C:/Users/|\\Users\\", "windows-user-path"),
    (r"/Users/|/home/", "unix-user-path"),
]

NON_PUBLIC_PATTERNS = [
    (r"confidential[:=]|internal only[:=]|do not publish[:=]", "non-public-keyword"),
    (r"不要公开[:：=]|机密[:：=]|内部专用[:：=]|草稿[:：=]", "non-public-keyword"),
]

TEMP_FILE_PATTERNS = [
    r"^~\$",
    r"\.tmp$",
    r"\.temp$",
    r"\.bak$",
    r"\.orig$",
    r"\.swp$",
    r"\.swo$",
    r"\.log$",
    r"\.cache$",
    r"\.pyc$",
    r"\.pyo$",
    r"^\.DS_Store$",
    r"^Thumbs\.db$",
    r"^desktop\.ini$",
]

TEMP_DIR_NAMES = {"__pycache__", ".pytest_cache", ".ipynb_checkpoints", ".mypy_cache", ".ruff_cache"}


def is_text_file(path: Path) -> bool:
    if path.name in {".gitignore", ".gitattributes"}:
        return True
    return path.suffix.lower() in TEXT_EXTENSIONS


def iter_files(root: Path):
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file():
            yield path


def add_finding(findings, severity, category, path, line=None, detail=None):
    item = {
        "severity": severity,
        "category": category,
        "path": str(path),
    }
    if line is not None:
        item["line"] = line
    if detail:
        item["detail"] = detail
    findings.append(item)


def scan_file(path: Path, root: Path, findings):
    rel = path.relative_to(root)
    name = path.name
    for pattern in TEMP_FILE_PATTERNS:
        if re.search(pattern, name, re.I):
            add_finding(findings, "high", "temporary-or-test-file", rel)
            break
    if any(part in TEMP_DIR_NAMES for part in path.parts):
        add_finding(findings, "high", "temporary-or-test-directory", rel)
    if not is_text_file(path):
        return
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        add_finding(findings, "medium", "non-utf8-text", rel)
        return
    if rel.as_posix() in {"scripts/audit_release_tree.py", "scripts/inspect_skill_dependencies.py"}:
        return
    groups = [
        ("high", "secret-or-token", SECRET_PATTERNS),
        ("medium", "personal-information", PRIVACY_PATTERNS),
        ("medium", "local-absolute-path", LOCAL_PATH_PATTERNS),
        ("medium", "non-public-content", NON_PUBLIC_PATTERNS),
    ]
    for line_no, line in enumerate(text.splitlines(), 1):
        for severity, category, patterns in groups:
            for pattern, label in patterns:
                if re.search(pattern, line, re.I):
                    add_finding(findings, severity, category, rel, line_no, label)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit a Codex skill release tree before publishing.")
    parser.add_argument("path", type=Path, help="Release tree to audit")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    root = args.path.resolve()
    if not root.exists() or not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    findings = []
    files = list(iter_files(root))
    for path in files:
        scan_file(path, root, findings)

    report = {
        "root": str(root),
        "file_count": len(files),
        "findings": findings,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Audited: {root}")
        print(f"Files: {len(files)}")
        if findings:
            print("Findings:")
            for item in findings:
                loc = item["path"]
                if "line" in item:
                    loc += f":{item['line']}"
                detail = f" ({item['detail']})" if "detail" in item else ""
                print(f"- [{item['severity']}] {item['category']}: {loc}{detail}")
        else:
            print("No findings.")

    return 1 if any(item["severity"] == "high" for item in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
