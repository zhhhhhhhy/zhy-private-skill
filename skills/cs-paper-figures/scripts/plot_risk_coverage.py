#!/usr/bin/env python3
"""Plot risk/error or accuracy against coverage from a validated CSV request."""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "cs-paper-figures-mpl"))
sys.dont_write_bytecode = True

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from _figure_common import (
    artifact_entry,
    build_package,
    load_json,
    output_dir_for,
    validate_request,
    write_json,
)


COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#7F7F7F"]
STYLES = ["-", "--", "-.", ":", "-"]
MARKERS = ["o", "s", "^", "D", "v"]


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


def read_rows(path: Path, y_metric: str) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"series", "coverage", y_metric}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            missing = sorted(required - set(reader.fieldnames or []))
            raise ValueError(f"missing_csv_columns:{','.join(missing)}")
        rows = []
        for index, raw in enumerate(reader):
            try:
                coverage = float(raw["coverage"])
                y_value = float(raw[y_metric])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"row_{index}_invalid_float") from exc
            if not 0 <= coverage <= 1 or not 0 <= y_value <= 1:
                raise ValueError(f"row_{index}_value_out_of_range")
            rows.append({"series": str(raw["series"]), "coverage": coverage, y_metric: y_value})
    if not rows:
        raise ValueError("empty_csv")
    return rows


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
    if request.get("figure_type") != "risk_coverage":
        validation["status"] = "fail"
        validation["errors"].append("unsupported_figure_type_for_script")
        return build_package(request, request_path, validation, transformation=Path(__file__), outputs=[])

    y_metric = str(request.get("y_metric", "error_rate"))
    if y_metric not in {"error_rate", "accuracy"}:
        raise ValueError("invalid_y_metric")
    source_path = Path(validation["normalized_sources"][0]["path"])
    rows = read_rows(source_path, y_metric)
    output_dir = output_dir_for(request, request_path)
    stem = str(request["artifact_id"])
    pdf = output_dir / f"{stem}.pdf"
    svg = output_dir / f"{stem}.svg"
    png = output_dir / f"{stem}.png"
    package_path = output_dir / "figure_package.json"
    ensure_free([pdf, svg, png, package_path], overwrite)
    output_dir.mkdir(parents=True, exist_ok=True)

    configure_style()
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["series"])].append(row)
    fig, ax = plt.subplots(figsize=(3.3, 2.45))
    for index, (series, values) in enumerate(sorted(grouped.items())):
        values.sort(key=lambda item: float(item["coverage"]))
        ax.plot(
            [float(item["coverage"]) for item in values],
            [float(item[y_metric]) for item in values],
            label=series,
            color=COLORS[index % len(COLORS)],
            linestyle=STYLES[index % len(STYLES)],
            marker=MARKERS[index % len(MARKERS)],
            linewidth=1.2,
            markersize=3,
        )
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("coverage")
    ax.set_ylabel("answered error" if y_metric == "error_rate" else "answered accuracy")
    ax.xaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.grid(color="#DDDDDD", linewidth=0.5)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(pdf)
    fig.savefig(svg)
    fig.savefig(png, dpi=300)
    plt.close(fig)

    outputs = [artifact_entry("pdf", pdf), artifact_entry("svg", svg), artifact_entry("png_preview", png)]
    package = build_package(request, request_path, validation, transformation=Path(__file__), outputs=outputs)
    package["plot_data"] = rows
    package["y_metric"] = y_metric
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
