#!/usr/bin/env python3
"""Bump the version in pyproject.toml following SemVer.

Usage:
    python scripts/bump_version.py patch   # 0.1.0 -> 0.1.1
    python scripts/bump_version.py minor   # 0.1.0 -> 0.2.0
    python scripts/bump_version.py major   # 0.1.0 -> 1.0.0

Prints the new version to stdout so CI can capture it.
"""

import argparse
import re
import sys
from pathlib import Path

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"
VERSION_RE = re.compile(r'^(version\s*=\s*")(\d+\.\d+\.\d+)(")', re.MULTILINE)


def bump(part: str) -> str:
    text = PYPROJECT.read_text()
    match = VERSION_RE.search(text)
    if not match:
        print("ERROR: Could not find version in pyproject.toml", file=sys.stderr)
        sys.exit(1)

    major, minor, patch = (int(x) for x in match.group(2).split("."))

    if part == "major":
        major, minor, patch = major + 1, 0, 0
    elif part == "minor":
        minor, patch = minor + 1, 0
    elif part == "patch":
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    new_text = VERSION_RE.sub(rf"\g<1>{new_version}\3", text)
    PYPROJECT.write_text(new_text)
    return new_version


def main():
    parser = argparse.ArgumentParser(description="Bump SemVer version in pyproject.toml")
    parser.add_argument("part", choices=["major", "minor", "patch"], help="Which part to bump")
    args = parser.parse_args()

    new_version = bump(args.part)
    print(new_version)


if __name__ == "__main__":
    main()
