
"""
VOXERA - Analytics API
=======================

Historical experiment analytics and reporting.
"""

from fastapi import APIRouter, HTTPException, Query

from app.evaluation.reports import (
    list_reports,
    get_report,
    build_summary,
    build_trends,
    compare_reports,
)


router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"],
)


@router.get("/summary")
def analytics_summary():
    """Return aggregate experiment statistics."""

    return {
        "status": "success",
        "summary": build_summary(),
    }


@router.get("/reports")
def analytics_reports(
    limit: int = Query(default=50, ge=1, le=1000),
):
    """List recent benchmark reports."""

    reports = list_reports(limit=limit)

    return {
        "status": "success",
        "total": len(reports),
        "reports": reports,
    }


@router.get("/reports/{report_id}")
def analytics_report(report_id: str):
    """Retrieve one benchmark report."""

    report = get_report(report_id)

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Experiment report not found.",
        )

    return {
        "status": "success",
        "report": report,
    }


@router.get("/trends")
def analytics_trends(
    limit: int = Query(default=50, ge=1, le=1000),
):
    """Return chronological experiment trends."""

    trends = build_trends(limit=limit)

    return {
        "status": "success",
        "total": len(trends),
        "trends": trends,
    }


@router.get("/compare")
def analytics_compare(
    report_ids: str = Query(
        ...,
        description="Comma-separated report identifiers.",
    ),
):
    """Compare selected experiment reports."""

    identifiers = [
        item.strip()
        for item in report_ids.split(",")
        if item.strip()
    ]

    try:
        reports = compare_reports(identifiers)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "status": "success",
        "total": len(reports),
        "reports": reports,
    }
