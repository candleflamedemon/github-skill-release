#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


TEXT_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".toml", ".json", ".py", ".sh", ".ps1"}
EXPLICIT_SKILL = re.compile(r"\$([a-z0-9][a-z0-9-]{1,62})\b")
PROSE_SKILL = re.compile(
    r"\b(?:use|uses|using|with|requires?|read|load)\s+(?:the\s+)?([A-Za-z][A-Za-z0-9 -]{1,80}?)\s+skill\b",
    re.I,
)


def is_text_file(path: Path) -> bool:
    return path.name in {"SKILL.md", "README.md"} or path.suffix.lower() in TEXT_EXTENSIONS


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def iter_candidate_files(root: Path):
    for path in root.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_file() and is_text_file(path):
            yield path


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect a Codex skill for references to other skills.")
    parser.add_argument("skill_path", type=Path, help="Skill directory to inspect")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    root = args.skill_path.resolve()
    if not root.exists() or not (root / "SKILL.md").exists():
        print(f"Not a Codex skill directory: {root}", file=sys.stderr)
        return 2

    own_name = None
    skill_header = (root / "SKILL.md").read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", skill_header, re.M)
    if match:
        own_name = match.group(1)

    bindings = []
    possible_dependencies = []
    for path in iter_candidate_files(root):
        rel = path.relative_to(root)
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            for match in EXPLICIT_SKILL.finditer(line):
                name = match.group(1)
                if name != own_name:
                    bindings.append(
                        {
                            "skill": name,
                            "relationship": "confirmed-binding",
                            "source": "explicit-dollar-reference",
                            "path": str(rel),
                            "line": line_no,
                        }
                    )
            for match in PROSE_SKILL.finditer(line):
                name = normalize_name(match.group(1))
                if name and name != own_name:
                    possible_dependencies.append(
                        {
                            "skill": name,
                            "relationship": "possible-dependency",
                            "source": "prose-skill-reference",
                            "path": str(rel),
                            "line": line_no,
                        }
                    )

    unique_bindings = {}
    for item in bindings:
        key = (item["skill"], item["source"], item["path"], item["line"])
        unique_bindings[key] = item
    unique_possible = {}
    for item in possible_dependencies:
        key = (item["skill"], item["source"], item["path"], item["line"])
        unique_possible[key] = item
    report = {
        "skill_path": str(root),
        "own_skill": own_name,
        "confirmed_bindings": sorted(unique_bindings.values(), key=lambda item: (item["skill"], item["path"], item["line"])),
        "possible_dependencies": sorted(unique_possible.values(), key=lambda item: (item["skill"], item["path"], item["line"])),
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Inspected: {root}")
        if own_name:
            print(f"Skill: {own_name}")
        if report["confirmed_bindings"]:
            print("Confirmed skill bindings:")
            for item in report["confirmed_bindings"]:
                print(f"- {item['skill']} [{item['source']}] {item['path']}:{item['line']}")
        else:
            print("No confirmed skill bindings found.")
        if report["possible_dependencies"]:
            print("Possible prose dependencies:")
            for item in report["possible_dependencies"]:
                print(f"- {item['skill']} [{item['source']}] {item['path']}:{item['line']}")
        else:
            print("No possible prose dependencies found.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
