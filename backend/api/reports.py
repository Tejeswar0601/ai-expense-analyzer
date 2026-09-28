"""
API routes for monthly reports. All endpoints require login and
scope everything to the current user.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.api.deps import get_current_user
from backend.services import analysis_service, ai_service, forecast_service, ai_insight_service, pdf_service

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/{year}/{month}")
def get_monthly_report(
    year: int, month: int, current_user: User = Depends(get_current_user)
):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Year looks invalid")

    return analysis_service.generate_monthly_report(year, month, current_user.id)


@router.post("/{year}/{month}/generate")
def generate_report_with_ai(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Same statistics as GET /{year}/{month}, plus AI-generated insights.
    If the AI call fails for any reason (bad/missing key, network issue,
    malformed response), the statistics are still returned - only the
    ai_insights section reflects the failure. Nothing crashes.

    On success, insights are also persisted (see ai_insight_service) so
    they can be viewed later via GET /{year}/{month}/insights without
    another Groq call. A persistence failure never blocks the response -
    the person still gets their insights even if saving them fails.
    """
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")
    if year < 2000 or year > 2100:
        raise HTTPException(status_code=400, detail="Year looks invalid")

    report = analysis_service.generate_monthly_report(year, month, current_user.id)

    if report["overall_summary"]["transaction_count"] == 0:
        raise HTTPException(
            status_code=400,
            detail="No expenses found for this month - nothing to analyze.",
        )

    try:
        report["ai_insights"] = ai_service.generate_ai_insights(report)
        report["ai_status"] = "success"

        try:
            month_year = f"{year:04d}-{month:02d}"
            ai_insight_service.save_insights(
                db,
                current_user.id,
                month_year,
                report["ai_insights"],
                report["overall_summary"]["transaction_count"],
            )
        except Exception:
            pass  # saving is best-effort; never block the response over it

    except ai_service.AIServiceError as e:
        report["ai_insights"] = None
        report["ai_status"] = "failed"
        report["ai_error"] = str(e)

    return report


@router.get("/{year}/{month}/insights")
def get_saved_insights(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns previously generated insights for this month, if any,
    without calling Groq again. 404 if nothing has been generated yet."""
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    month_year = f"{year:04d}-{month:02d}"
    saved = ai_insight_service.get_saved_insights(db, current_user.id, month_year)
    if saved is None:
        raise HTTPException(status_code=404, detail="No saved insights for this month yet.")
    return saved


@router.get("/{year}/{month}/forecast")
def get_month_forecast(
    year: int, month: int, current_user: User = Depends(get_current_user)
):
    """
    Projects month-end spending based on the daily average rate so far.
    Only meaningful for the current, in-progress month - returns
    available=False for any other month rather than fabricating a
    projection for a month that's already over.
    """
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    df = analysis_service.get_month_dataframe(year, month, current_user.id)
    return forecast_service.compute_forecast(df, year, month)


@router.get("/{year}/{month}/pdf")
def download_report_pdf(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Downloads the monthly report as a PDF: stats, category chart,
    trends, alerts, and AI insights if they've already been generated
    for this month (this endpoint never calls Groq itself).
    """
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    report = analysis_service.generate_monthly_report(year, month, current_user.id)
    if report["overall_summary"]["transaction_count"] == 0:
        raise HTTPException(
            status_code=400, detail="No expenses found for this month - nothing to export."
        )

    month_year = f"{year:04d}-{month:02d}"
    saved_insights = ai_insight_service.get_saved_insights(db, current_user.id, month_year)

    pdf_buffer = pdf_service.generate_report_pdf(report, saved_insights, current_user.full_name)

    filename = f"expense_report_{month_year}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
