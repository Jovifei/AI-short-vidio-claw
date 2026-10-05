#!/usr/bin/env python3
"""Validate a JSON document against a repository JSON Schema."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--schema", required=True)
    p.add_argument("--input", required=True)
    args = p.parse_args()

    schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    data = json.loads(Path(args.input).read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    if errors:
        for e in errors:
            path = ".".join(str(x) for x in e.path) or "<root>"
            print(f"ERROR {path}: {e.message}")
        return 2

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
