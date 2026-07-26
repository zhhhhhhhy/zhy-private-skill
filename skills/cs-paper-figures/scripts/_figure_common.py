#!/usr/bin/env python3
"""Shared contract and provenance helpers for cs-paper-figures."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUEST_SCHEMA = "cs-paper-figure-request-v1"
PACKAGE_SCHEMA = "cs-paper-figure-package-v1"
FIGURE_TYPES = {
    "selection_gap_accounting",
    "risk_coverage",
    "cross_dataset_transfer",
    "decision_layer_schematic",
}
SOURCE_KINDS = {"empirical", "diagnostic", "conceptual"}
SPLIT_ROLES = {
    "train",
    "validation",
    "test",
    "frozen_heldout",
    "oracle_diagnostic",
    "hard_slice",
    "not_applicable",
}
LABEL_CLASSES = {
    "gold",
    "teacher",
    "weak",
    "oracle",
    "heuristic",
    "project_adjudicated",
    "mixed",
    "not_applicable",
}
ORACLE_STATUSES = {"none", "diagnostic_only", "leaky"}
OVERCLAIM_RE = re.compile(
    r"\b(solves?|proved?|proves?|guarantees?|state[- ]of[- ]the[- ]art|sota|"
    r"generalizes?|universally|causes?)\b|"
    r"(?:彻底解决|解决了|证明了?|保证|最先进|泛化到所有|普遍适用|因果|导致)",
    re.IGNORECASE,
)
MISLABELED_GOLD_RE = re.compile(
    r"\b(teacher|weak|heuristic|oracle|pseudo|project[-_ ]adjudicated|agent[-_ ]assisted)\b|"
    r"(?:教师标签|弱标签|启发式|预言机|伪标签|项目裁定|智能体辅助)",
    re.IGNORECASE,
)


Json = dict[str, Any]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Json:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("request_root_must_be_object")
    return value


def resolve_request_path(request_path: Path, value: str | Path) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    request_relative = (request_path.parent / candidate).resolve()
    if request_relative.exists():
        return request_relative
    return (Path.cwd() / candidate).resolve()


def output_dir_for(request: Json, request_path: Path) -> Path:
    value = request.get("output_dir")
    if not isinstance(value, str) or not value.strip():
        return request_path.parent.resolve()
    return resolve_request_path(request_path, value)


def split_roles(request: Json) -> list[str]:
    raw = request.get("split_role")
    roles = raw if isinstance(raw, list) else [raw]
    for item in request.get("source_data", []) if isinstance(request.get("source_data"), list) else []:
        if isinstance(item, dict) and item.get("split_role") is not None:
            value = item["split_role"]
            roles.extend(value if isinstance(value, list) else [value])
    return sorted({str(role) for role in roles if role is not None})


def denominator_valid(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, dict) and value:
        return all(
            isinstance(item, (int, float)) and not isinstance(item, bool) and item > 0
            for item in value.values()
        )
    return False


def validate_request(request: Json, request_path: Path, *, overwrite: bool = False) -> Json:
    errors: list[str] = []
    warnings: list[str] = []

    if request.get("schema_version") != REQUEST_SCHEMA:
        errors.append("invalid_schema_version")
    artifact_id = request.get("artifact_id")
    if not isinstance(artifact_id, str) or re.fullmatch(r"[a-z0-9][a-z0-9_-]*", artifact_id) is None:
        errors.append("invalid_artifact_id")
    if not isinstance(request.get("venue"), str) or not request.get("venue", "").strip():
        errors.append("missing_venue")
    if request.get("figure_type") not in FIGURE_TYPES:
        errors.append("invalid_figure_type")
    if request.get("source_kind") not in SOURCE_KINDS:
        errors.append("invalid_source_kind")
    if request.get("label_class") not in LABEL_CLASSES:
        errors.append("invalid_label_class")
    if not isinstance(request.get("label_source"), str) or not request.get("label_source", "").strip():
        errors.append("missing_label_source")
    if request.get("oracle_status") not in ORACLE_STATUSES:
        errors.append("invalid_oracle_status")
    if not isinstance(request.get("caption_claim"), str) or not request.get("caption_claim", "").strip():
        errors.append("missing_caption_claim")
    if not isinstance(request.get("caveats"), list):
        errors.append("caveats_must_be_list")
    if not isinstance(request.get("output_dir"), str) or not request.get("output_dir", "").strip():
        errors.append("missing_output_dir")

    roles = split_roles(request)
    if not roles or any(role not in SPLIT_ROLES for role in roles):
        errors.append("invalid_split_role")

    source_kind = request.get("source_kind")
    source_data = request.get("source_data", [])
    normalized_sources: list[Json] = []
    normalized_transformations: list[Json] = []
    if source_kind in {"empirical", "diagnostic"}:
        if not isinstance(source_data, list) or not source_data:
            errors.append("missing_source_data")
        if not denominator_valid(request.get("denominator")):
            errors.append("missing_or_invalid_denominator")
        if not isinstance(request.get("metrics"), list) or not request.get("metrics"):
            errors.append("missing_metrics")
    elif source_kind == "conceptual":
        if not isinstance(request.get("claim_boundary"), str) or not request.get("claim_boundary", "").strip():
            errors.append("conceptual_missing_claim_boundary")
        if request.get("label_class") != "not_applicable":
            errors.append("conceptual_label_class_must_be_not_applicable")
        if roles != ["not_applicable"]:
            errors.append("conceptual_split_role_must_be_not_applicable")

    if isinstance(source_data, list):
        for index, item in enumerate(source_data):
            if not isinstance(item, dict):
                errors.append(f"source_data_{index}_must_be_object")
                continue
            value = item.get("path")
            expected_hash = item.get("sha256")
            if not isinstance(value, str) or not value.strip():
                errors.append(f"source_data_{index}_missing_path")
                continue
            if not isinstance(expected_hash, str) or re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash) is None:
                errors.append(f"source_data_{index}_missing_or_invalid_sha256")
                continue
            path = resolve_request_path(request_path, value)
            if not path.is_file():
                errors.append(f"source_data_{index}_missing_file")
                continue
            actual_hash = sha256_file(path)
            if actual_hash.lower() != expected_hash.lower():
                errors.append(f"source_data_{index}_sha256_mismatch")
            normalized_sources.append(
                {
                    **item,
                    "path": str(path),
                    "sha256": actual_hash,
                }
            )

    data_transformations = request.get("data_transformations", [])
    if data_transformations is not None and not isinstance(data_transformations, list):
        errors.append("data_transformations_must_be_list")
    elif isinstance(data_transformations, list):
        for index, item in enumerate(data_transformations):
            if not isinstance(item, dict):
                errors.append(f"data_transformation_{index}_must_be_object")
                continue
            value = item.get("path")
            expected_hash = item.get("sha256")
            if not isinstance(value, str) or not value.strip():
                errors.append(f"data_transformation_{index}_missing_path")
                continue
            if not isinstance(expected_hash, str) or re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash) is None:
                errors.append(f"data_transformation_{index}_missing_or_invalid_sha256")
                continue
            path = resolve_request_path(request_path, value)
            if not path.is_file():
                errors.append(f"data_transformation_{index}_missing_file")
                continue
            actual_hash = sha256_file(path)
            if actual_hash.lower() != expected_hash.lower():
                errors.append(f"data_transformation_{index}_sha256_mismatch")
            normalized_transformations.append({**item, "path": str(path), "sha256": actual_hash})

    surface_provenance = request.get("surface_provenance")
    if request.get("label_class") == "mixed":
        if not isinstance(surface_provenance, dict) or not surface_provenance:
            errors.append("mixed_label_class_requires_surface_provenance")
    if isinstance(surface_provenance, dict):
        provenance_roles: set[str] = set()
        for surface, provenance in surface_provenance.items():
            if not isinstance(surface, str) or not surface or not isinstance(provenance, dict):
                errors.append("invalid_surface_provenance_entry")
                continue
            role = provenance.get("split_role")
            label_class = provenance.get("label_class")
            label_source = provenance.get("label_source")
            oracle_status = provenance.get("oracle_status", request.get("oracle_status"))
            if role not in SPLIT_ROLES:
                errors.append(f"surface_provenance_invalid_split_role:{surface}")
            else:
                provenance_roles.add(str(role))
            if label_class not in LABEL_CLASSES - {"mixed"}:
                errors.append(f"surface_provenance_invalid_label_class:{surface}")
            if not isinstance(label_source, str) or not label_source.strip():
                errors.append(f"surface_provenance_missing_label_source:{surface}")
            if oracle_status not in ORACLE_STATUSES:
                errors.append(f"surface_provenance_invalid_oracle_status:{surface}")
            if label_class == "gold" and MISLABELED_GOLD_RE.search(str(label_source or "")):
                errors.append(f"surface_provenance_non_gold_mislabeled_as_gold:{surface}")
            if label_class == "oracle" and oracle_status == "none":
                errors.append(f"surface_provenance_oracle_declared_non_oracle:{surface}")
        if roles and provenance_roles and set(roles) != provenance_roles:
            errors.append("surface_provenance_split_roles_mismatch")
        denominator = request.get("denominator")
        if request.get("figure_type") == "cross_dataset_transfer" and isinstance(denominator, dict):
            if set(surface_provenance) != set(denominator):
                errors.append("surface_provenance_denominator_keys_mismatch")
    if request.get("profile") == "reportfill" and len(roles) > 1:
        mixed_allowed = (
            request.get("figure_type") == "cross_dataset_transfer"
            and request.get("surface_role_separation") is True
            and isinstance(surface_provenance, dict)
            and bool(surface_provenance)
        )
        if not mixed_allowed:
            errors.append("reportfill_mixed_split_roles")
    if request.get("label_class") == "gold" and MISLABELED_GOLD_RE.search(str(request.get("label_source", ""))):
        errors.append("non_gold_source_mislabeled_as_gold")
    if request.get("label_class") == "oracle" and request.get("oracle_status") == "none":
        errors.append("oracle_label_declared_non_oracle")
    if request.get("label_class") == "gold" and request.get("oracle_status") != "none":
        errors.append("gold_label_has_oracle_status")
    caveats = request.get("caveats") if isinstance(request.get("caveats"), list) else []
    if OVERCLAIM_RE.search(str(request.get("caption_claim", ""))) and not caveats:
        errors.append("caption_overclaim_requires_caveat")

    planned = request.get("planned_outputs", [])
    if planned is not None and not isinstance(planned, list):
        errors.append("planned_outputs_must_be_list")
    elif isinstance(planned, list) and not overwrite:
        for index, value in enumerate(planned):
            if not isinstance(value, str):
                errors.append(f"planned_output_{index}_must_be_string")
                continue
            if resolve_request_path(request_path, value).exists():
                errors.append(f"planned_output_{index}_exists_without_overwrite")

    if source_kind == "conceptual" and source_data:
        warnings.append("conceptual_source_data_present")
    if str(request.get("venue", "")).lower() not in {"aaai", "template-derived"}:
        warnings.append("venue_profile_must_be_derived_from_live_template")

    return {
        "status": "pass" if not errors else "fail",
        "errors": sorted(set(errors)),
        "warnings": sorted(set(warnings)),
        "normalized_sources": normalized_sources,
        "normalized_transformations": normalized_transformations,
        "split_roles": roles,
    }


def artifact_entry(kind: str, path: Path) -> Json:
    return {
        "kind": kind,
        "path": str(path.resolve()),
        "sha256": sha256_file(path),
    }


def build_package(
    request: Json,
    request_path: Path,
    validation: Json,
    *,
    transformation: Path,
    outputs: list[Json],
) -> Json:
    return {
        "schema_version": PACKAGE_SCHEMA,
        "created_at": now_iso(),
        "status": validation["status"],
        "artifact_id": request.get("artifact_id"),
        "venue": request.get("venue"),
        "figure_type": request.get("figure_type"),
        "source_kind": request.get("source_kind"),
        "request": {
            "path": str(request_path.resolve()),
            "sha256": sha256_file(request_path),
        },
        "source_data": validation.get("normalized_sources", []),
        "data_transformations": validation.get("normalized_transformations", []),
        "transformation": {
            "script": str(transformation.resolve()),
            "sha256": sha256_file(transformation),
        },
        "outputs": outputs,
        "claim_trace": {
            "caption_claim": request.get("caption_claim"),
            "metrics": request.get("metrics", []),
            "source_paths": [item["path"] for item in validation.get("normalized_sources", [])],
            "surface_provenance": request.get("surface_provenance", {}),
        },
        "limitations": request.get("caveats", []),
        "claim_boundary": request.get("claim_boundary"),
        "validation": {
            "status": validation["status"],
            "errors": validation.get("errors", []),
            "warnings": validation.get("warnings", []),
            "split_roles": validation.get("split_roles", []),
        },
        "execution": {
            "cpu_only": True,
            "api_calls": 0,
            "model_calls": 0,
            "gpu_commands": 0,
            "download_commands": 0,
            "external_cost_usd": 0,
        },
    }


def write_json(path: Path, payload: Json, *, overwrite: bool = False) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"output_exists_without_overwrite:{path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
