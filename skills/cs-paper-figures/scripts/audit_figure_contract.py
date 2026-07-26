#!/usr/bin/env python3
"""Validate a cs-paper-figures request and emit a zero-cost package record."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from _figure_common import build_package, load_json, output_dir_for, validate_request, write_json


def run(request_path: Path, *, package_path: Path | None, overwrite: bool) -> dict:
    request_path = request_path.resolve()
    request = load_json(request_path)
    validation = validate_request(request, request_path, overwrite=overwrite)
    target = package_path.resolve() if package_path else output_dir_for(request, request_path) / "figure_package.json"
    package = build_package(
        request,
        request_path,
        validation,
        transformation=Path(__file__),
        outputs=[],
    )
    if validation["status"] == "pass":
        try:
            write_json(target, package, overwrite=overwrite)
        except FileExistsError:
            validation["status"] = "fail"
            validation["errors"].append("package_exists_without_overwrite")
            package["status"] = "fail"
            package["validation"] = {
                "status": "fail",
                "errors": validation["errors"],
                "warnings": validation["warnings"],
                "split_roles": validation["split_roles"],
            }
    package["package_path"] = str(target)
    return package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--package-path", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    package = run(args.request, package_path=args.package_path, overwrite=args.overwrite)
    print(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if package["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
