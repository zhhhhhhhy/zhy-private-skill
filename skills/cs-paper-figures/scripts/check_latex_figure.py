#!/usr/bin/env python3
"""Statically check a TikZ/LaTeX figure and optionally compile standalone TeX."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


UNSAFE_PATTERNS = {
    "shell_escape": re.compile(r"\\write18|\\ShellEscape", re.IGNORECASE),
    "file_write": re.compile(r"\\(?:openout|write|immediate)\b", re.IGNORECASE),
    "remote_url": re.compile(r"https?://", re.IGNORECASE),
}


def strip_comments(text: str) -> str:
    return "\n".join(line.split("%", 1)[0] for line in text.splitlines())


def brace_balance(text: str) -> int:
    cleaned = re.sub(r"\\[{}]", "", strip_comments(text))
    return cleaned.count("{") - cleaned.count("}")


def run(source: Path, *, compile_requested: bool) -> dict:
    source = source.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    if not source.is_file():
        return {"status": "fail", "errors": ["missing_source"], "warnings": []}
    text = source.read_text(encoding="utf-8")
    unsafe = [name for name, pattern in UNSAFE_PATTERNS.items() if pattern.search(text)]
    if unsafe:
        errors.extend(f"unsafe_latex:{name}" for name in unsafe)
    if brace_balance(text) != 0:
        errors.append("unbalanced_braces")
    if "\\begin{tikzpicture}" not in text and "\\includegraphics" not in text:
        warnings.append("no_tikz_or_includegraphics_found")
    standalone = "\\documentclass" in text and "\\begin{document}" in text
    pdflatex = shutil.which("pdflatex")
    compile_status = "not_requested"
    compile_log_tail = ""
    if compile_requested and not errors:
        if pdflatex is None:
            compile_status = "tool_unavailable"
        elif not standalone:
            compile_status = "fragment_requires_parent_document"
        else:
            with tempfile.TemporaryDirectory(prefix="cs-paper-figures-tex-") as temp:
                temp_dir = Path(temp)
                copied = temp_dir / source.name
                shutil.copy2(source, copied)
                completed = subprocess.run(
                    [
                        pdflatex,
                        "-no-shell-escape",
                        "-interaction=nonstopmode",
                        "-halt-on-error",
                        copied.name,
                    ],
                    cwd=temp_dir,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    timeout=60,
                    check=False,
                )
                compile_log_tail = "\n".join(completed.stdout.splitlines()[-20:])
                compile_status = "pass" if completed.returncode == 0 else "fail"
                if completed.returncode != 0:
                    errors.append("latex_compile_failed")
    status = "fail" if errors else "pass"
    return {
        "schema_version": "cs-paper-latex-check-v1",
        "status": status,
        "source": str(source),
        "static": {
            "brace_balance": brace_balance(text),
            "standalone": standalone,
            "unsafe_patterns": unsafe,
        },
        "compile": {
            "requested": compile_requested,
            "pdflatex": pdflatex,
            "status": compile_status,
            "log_tail": compile_log_tail,
            "shell_escape": False,
        },
        "errors": errors,
        "warnings": warnings,
        "execution": {
            "api_calls": 0,
            "model_calls": 0,
            "gpu_commands": 0,
            "download_commands": 0,
            "external_cost_usd": 0,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--compile", action="store_true")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    payload = run(args.source, compile_requested=args.compile)
    if args.output_json:
        if args.output_json.exists() and not args.overwrite:
            payload["status"] = "fail"
            payload["errors"].append("output_exists_without_overwrite")
        else:
            args.output_json.parent.mkdir(parents=True, exist_ok=True)
            args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
