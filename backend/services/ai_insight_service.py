"""
Persists AI-generated insights so they can be retrieved later without
re-calling Groq.

Confidence score is deliberately NOT taken from the AI's own output -
LLMs self-reporting confidence is unreliable and would amount to the
AI inventing a number. Instead it's derived here from something real:
how many transactions backed the analysis.
"""

from typing import Optional

from sqlalchemy.orm import Session
from backend.models.ai_insight import AIInsight

SINGULAR_TYPES = [
    "spending_summary", "spending_patterns", "main_expense_categories", "monthly_summary",
]

# Confidence reaches 1.0 once at least this many transactions backed the analysis.
FULL_CONFIDENCE_TRANSACTION_COUNT = 15


def compute_confidence(transaction_count: int) -> float:
    """More transactions supporting the analysis -> higher confidence."""
    if transaction_count <= 0:
        return 0.0
    return round(min(transaction_count / FULL_CONFIDENCE_TRANSACTION_COUNT, 1.0), 2)


def save_insights(
    db: Session, user_id: int, month_year: str, ai_insights: dict, transaction_count: int
) -> None:
    """Replaces any previously saved insights for this user/month with
    the freshly generated set (so re-generating doesn't pile up old
    versions - only the latest snapshot is kept)."""
    confidence = compute_confidence(transaction_count)

    db.query(AIInsight).filter(
        AIInsight.user_id == user_id, AIInsight.month_year == month_year
    ).delete()

    rows = [
        AIInsight(
            user_id=user_id,
            month_year=month_year,
            insight_type=field,
            message=ai_insights[field],
            confidence_score=confidence,
        )
        for field in SINGULAR_TYPES
        if field in ai_insights
    ]
    for rec in ai_insights.get("recommendations", []):
        rows.append(AIInsight(
            user_id=user_id,
            month_year=month_year,
            insight_type="recommendation",
            message=rec,
            confidence_score=confidence,
        ))

    db.add_all(rows)
    db.commit()


def get_saved_insights(db: Session, user_id: int, month_year: str) -> Optional[dict]:
    rows = (
        db.query(AIInsight)
        .filter(AIInsight.user_id == user_id, AIInsight.month_year == month_year)
        .all()
    )
    if not rows:
        return None

    result = {"recommendations": [], "confidence_score": None, "generated_at": None}
    for row in rows:
        if row.insight_type == "recommendation":
            result["recommendations"].append(row.message)
        else:
            result[row.insight_type] = row.message

        if row.confidence_score is not None:
            result["confidence_score"] = float(row.confidence_score)
        if result["generated_at"] is None or row.created_at > result["generated_at"]:
            result["generated_at"] = row.created_at

    return result
