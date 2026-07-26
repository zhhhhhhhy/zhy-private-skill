#!/usr/bin/env python3
"""Plot selection-gap or cross-dataset accounting from a validated CSV request."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "cs-paper-figures-mpl"))
sys.dont_write_bytecode = True

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from _figure_common import (
    artifact_entry,
    build_package,
    load_json,
    output_dir_for,
    validate_request,
    write_json,
)


COLORS = ["#0072B2", "#D55E00", "#B3B3B3"]
REQUIRED_COLUMNS = {"surface", "final_correct", "selection_gap", "candidate_miss", "n"}


def configure_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "font.size": 8,
            "axes.labelsize": 8,
            "xtick.labelsize": 7,
            "ytick.labelsize": 7,
            "legend.fontsize": 7,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "savefig.bbox": "tight",
        }
    )


def read_rows(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not REQUIRED_COLUMNS.issubset(reader.fieldnames):
            missing = sorted(REQUIRED_COLUMNS - set(reader.fieldnames or []))
            raise ValueError(f"missing_csv_columns:{','.join(missing)}")
        rows = []
        for index, raw in enumerate(reader):
            try:
                final = int(raw["final_correct"])
                gap = int(raw["selection_gap"])
                miss = int(raw["candidate_miss"])
                n = int(raw["n"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"row_{index}_invalid_integer") from exc
            if n <= 0 or min(final, gap, miss) < 0 or final + gap + miss != n:
                raise ValueError(f"row_{index}_invalid_accounting")
            rows.append(
                {
                    "surface": str(raw["surface"]),
                    "final_correct": final,
                    "selection_gap": gap,
                    "candidate_miss": miss,
                    "n": n,
                }
            )
    if not rows:
        raise ValueError("empty_csv")
    return rows


def check_denominators(rows: list[dict[str, object]], denominator: object) -> None:
    if isinstance(denominator, (int, float)) and not isinstance(denominator, bool):
        if any(int(row["n"]) != int(denominator) for row in rows):
            raise ValueError("request_denominator_mismatch")
    elif isinstance(denominator, dict):
        for row in rows:
            surface = str(row["surface"])
            if surface not in denominator or int(denominator[surface]) != int(row["n"]):
                raise ValueError(f"request_denominator_mismatch:{surface}")


def ensure_free(paths: list[Path], overwrite: bool) -> None:
    if overwrite:
        return
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        raise FileExistsError("output_exists_without_overwrite:" + ",".join(existing))


def run(request_path: Path, *, overwrite: bool = False) -> dict:
    request_path = request_path.resolve()
    request = load_json(request_path)
    validation = validate_request(request, request_path, overwrite=overwrite)
    if validation["status"] != "pass":
        return build_package(request, request_path, validation, transformation=Path(__file__), outputs=[])
    if request.get("figure_type") not in {"selection_gap_accounting", "cross_dataset_transfer"}:
        validation["status"] = "fail"
        validation["errors"].append("unsupported_figure_type_for_script")
        return build_package(request, request_path, validation, transformation=Path(__file__), outputs=[])

    source_path = Path(validation["normalized_sources"][0]["path"])
    rows = read_rows(source_path)
    check_denominators(rows, request.get("denominator"))
    output_dir = output_dir_for(request, request_path)
    stem = str(request["artifact_id"])
    pdf = output_dir / f"{stem}.pdf"
    svg = output_dir / f"{stem}.svg"
    png = output_dir / f"{stem}.png"
    package_path = output_dir / "figure_package.json"
    ensure_free([pdf, svg, png, package_path], overwrite)
    output_dir.mkdir(parents=True, exist_ok=True)

    configure_style()
    labels = [str(row["surface"]) for row in rows]
    final = np.array([int(row["final_correct"]) / int(row["n"]) for row in rows])
    gap = np.array([int(row["selection_gap"]) / int(row["n"]) for row in rows])
    miss = np.array([int(row["candidate_miss"]) / int(row["n"]) for row in rows])
    y = np.arange(len(rows))
    height = max(1.8, 0.43 * len(rows) + 0.75)
    fig, ax = plt.subplots(figsize=(6.6, height))
    ax.barh(y, final, color=COLORS[0], label="final correct", edgecolor="white", linewidth=0.4)
    ax.barh(y, gap, left=final, color=COLORS[1], label="selection gap", edgecolor="white", linewidth=0.4)
    ax.barh(y, miss, left=final + gap, color=COLORS[2], label="candidate miss", edgecolor="white", linewidth=0.4)
    for index, row in enumerate(rows):
        segments = [int(row["final_correct"]), int(row["selection_gap"]), int(row["candidate_miss"])]
        starts = [0.0, final[index], final[index] + gap[index]]
        widths = [final[index], gap[index], miss[index]]
        for value, start, width in zip(segments, starts, widths):
            if width >= 0.08:
                ax.text(start + width / 2, index, str(value), ha="center", va="center", fontsize=7)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of evaluation set")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.legend(frameon=False, ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01))
    ax.grid(axis="x", color="#DDDDDD", linewidth=0.5)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(pdf)
    fig.savefig(svg)
    fig.savefig(png, dpi=300)
    plt.close(fig)

    outputs = [artifact_entry("pdf", pdf), artifact_entry("svg", svg), artifact_entry("png_preview", png)]
    package = build_package(request, request_path, validation, transformation=Path(__file__), outputs=outputs)
    package["plot_data"] = rows
    write_json(package_path, package, overwrite=overwrite)
    package["package_path"] = str(package_path.resolve())
    return package


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        package = run(args.request, overwrite=args.overwrite)
    except (FileExistsError, ValueError) as exc:
        print(json.dumps({"status": "fail", "errors": [str(exc)]}, indent=2))
        return 1
    print(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if package["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
