
"""
VOXERA - Experiment Report Repository
======================================

Responsibilities:
- Persist benchmark reports
- Generate unique report identifiers
- Discover historical reports
- Retrieve individual experiments
- Aggregate experiment statistics
"""

import json
import uuid

from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Always resolve storage relative to the backend directory.
BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]

REPORT_DIRECTORY = (
    BACKEND_DIRECTORY / "experiments" / "reports"
)


def ensure_report_directory() -> None:
    """Create report storage if it does not exist."""
    REPORT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )


def save_report(
    benchmark: dict,
    experiment_name: str = "voxera_ab_test",
) -> Path:
    """Persist a benchmark and return its file path."""

    ensure_report_directory()

    now = datetime.now(timezone.utc)

    safe_name = "".join(
        character if character.isalnum() or character in "-_"
        else "_"
        for character in experiment_name
    ).strip("_") or "experiment"

    report_id = (
        f"{safe_name}_"
        f"{now.strftime('%Y%m%d_%H%M%S_%f')}_"
        f"{uuid.uuid4().hex[:8]}"
    )

    report = {
        "report_id": report_id,
        "experiment_name": experiment_name,
        "created_at": now.isoformat(),
        "benchmark": benchmark,
    }

    output_path = REPORT_DIRECTORY / f"{report_id}.json"
    temporary_path = REPORT_DIRECTORY / f".{report_id}.tmp"

    try:
        with temporary_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                report,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_path.replace(output_path)

    finally:
        if temporary_path.exists():
            temporary_path.unlink()

    return output_path


def list_reports(
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Return recent report metadata."""

    ensure_report_directory()

    reports = []

    paths = sorted(
        REPORT_DIRECTORY.glob("*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    for path in paths:

        if len(reports) >= limit:
            break

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                report = json.load(file)

            benchmark = report.get("benchmark", {})

            reports.append({
                "report_id": report.get(
                    "report_id",
                    path.stem,
                ),
                "experiment_name": report.get(
                    "experiment_name",
                    "unknown",
                ),
                "created_at": report.get("created_at"),
                "baseline_wer": (
                    benchmark.get("baseline", {})
                    .get("wer", {}).get("wer")
                ),
                "enhanced_wer": (
                    benchmark.get("enhanced", {})
                    .get("wer", {}).get("wer")
                ),
                "baseline_f1": (
                    benchmark.get("baseline", {})
                    .get("technical_metrics", {})
                    .get("f1_score")
                ),
                "enhanced_f1": (
                    benchmark.get("enhanced", {})
                    .get("technical_metrics", {})
                    .get("f1_score")
                ),
            })

        except (OSError, json.JSONDecodeError):
            # Ignore corrupted reports without breaking discovery.
            continue

    return reports


def get_report(
    report_id: str,
) -> dict[str, Any] | None:
    """Retrieve one report by its identifier."""

    # Prevent directory traversal.
    if (
        not report_id
        or Path(report_id).name != report_id
        or "/" in report_id
        or "\\" in report_id
    ):
        return None

    ensure_report_directory()

    report_path = REPORT_DIRECTORY / f"{report_id}.json"

    if not report_path.is_file():
        return None

    try:
        with report_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            report = json.load(file)

        report.setdefault("report_id", report_id)

        return report

    except (OSError, json.JSONDecodeError):
        return None


def _mean(values: list[float]) -> float | None:
    """Calculate a mean without failing on empty data."""

    return (
        sum(values) / len(values)
        if values
        else None
    )


def build_summary() -> dict[str, Any]:
    """Aggregate statistics across valid reports."""

    reports = list_reports(limit=100000)

    baseline_wer = [
        report["baseline_wer"]
        for report in reports
        if report["baseline_wer"] is not None
    ]

    enhanced_wer = [
        report["enhanced_wer"]
        for report in reports
        if report["enhanced_wer"] is not None
    ]

    baseline_f1 = [
        report["baseline_f1"]
        for report in reports
        if report["baseline_f1"] is not None
    ]

    enhanced_f1 = [
        report["enhanced_f1"]
        for report in reports
        if report["enhanced_f1"] is not None
    ]

    return {
        "total_reports": len(reports),
        "average_baseline_wer": _mean(baseline_wer),
        "average_enhanced_wer": _mean(enhanced_wer),
        "average_baseline_f1": _mean(baseline_f1),
        "average_enhanced_f1": _mean(enhanced_f1),
        "reports_with_wer": len(baseline_wer),
        "reports_with_f1": len(baseline_f1),
    }


def build_trends(
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Return chronological experiment measurements."""

    reports = list_reports(limit=limit)

    trends = []

    for report in reversed(reports):
        trends.append({
            "report_id": report["report_id"],
            "created_at": report["created_at"],
            "baseline_wer": report["baseline_wer"],
            "enhanced_wer": report["enhanced_wer"],
            "baseline_f1": report["baseline_f1"],
            "enhanced_f1": report["enhanced_f1"],
        })

    return trends


def compare_reports(
    report_ids: list[str],
) -> list[dict[str, Any]]:
    """Retrieve selected reports for side-by-side comparison."""

    if not report_ids:
        raise ValueError("At least one report ID is required.")

    if len(report_ids) > 20:
        raise ValueError("Maximum 20 reports per comparison.")

    results = []

    for report_id in report_ids:
        report = get_report(report_id)

        if report is None:
            raise ValueError(
                f"Report not found or invalid: {report_id}"
            )

        results.append(report)

    return results
