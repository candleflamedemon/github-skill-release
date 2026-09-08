#!/usr/bin/env python3
import argparse
import re
import sys


VERSION = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")


def parse_version(value: str):
    match = VERSION.match(value.strip())
    if not match:
        raise ValueError("version must look like v1.2.3 or 1.2.3")
    return [int(match.group(1)), int(match.group(2)), int(match.group(3))]


def bump(parts, kind: str):
    major, minor, patch = parts
    if kind == "major":
        return [major + 1, 0, 0]
    if kind == "minor":
        return [major, minor + 1, 0]
    if kind == "patch":
        return [major, minor, patch + 1]
    raise ValueError("bump must be major, minor, or patch")


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest the next GitHub Release version tag.")
    parser.add_argument("current", help="Current version tag, such as v1.1.1")
    parser.add_argument("bump", choices=["major", "minor", "patch"], help="Version bump type")
    args = parser.parse_args()

    try:
        next_version = bump(parse_version(args.current), args.bump)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"v{next_version[0]}.{next_version[1]}.{next_version[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
