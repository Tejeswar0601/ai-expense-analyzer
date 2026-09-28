"""
AI service: turns already-calculated statistics into natural-language
insights and recommendations using Groq.

IMPORTANT: this file never calculates financial numbers. It only takes
the output of analysis_service.py and asks the AI to explain it in
plain language. This matches the project spec - Pandas computes,
the AI explains.
"""

import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "openai/gpt-oss-20b"

_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SYSTEM_PROMPT = """You are a helpful personal finance assistant.

You will be given ALREADY-CALCULATED spending statistics for one month.
Do not invent, estimate, or recalculate any numbers - only reference the
figures given to you, exactly as provided.

Respond ONLY with a JSON object with exactly these keys:
{
  "spending_summary": "2-4 sentences explaining overall spending",
  "spending_patterns": "2-4 sentences identifying meaningful patterns",
  "main_expense_categories": "2-4 sentences on where money went",
  "recommendations": ["short practical tip", "short practical tip", "short practical tip"],
  "monthly_summary": "1-2 sentence natural-language summary"
}

Base recommendations only on the data given. Do not include any text
outside the JSON object."""


class AIServiceError(Exception):
    """Raised when the AI request fails or returns something unusable."""
    pass


def build_prompt(report: dict) -> str:
    """Turn the calculated report dict into a plain-text prompt for the AI."""
    summary = report["overall_summary"]
    categories = report["category_analysis"]
    trends = report["trends"]
    comparison = report["previous_month_comparison"]
    unusual = report["unusual_transactions"]

    lines = [
        f"Month: {report['month_name']}",
        f"Total spending: Rs. {summary['total_spending']:,.2f}",
        f"Number of transactions: {summary['transaction_count']}",
        f"Average transaction: Rs. {summary['average_transaction']:,.2f}",
        f"Average daily spending: Rs. {summary['average_daily_spending']:,.2f}",
        "",
        "Category breakdown:",
    ]
    for cat in categories:
        lines.append(f"- {cat['category']}: Rs. {cat['total']:,.2f} ({cat['percentage']}%)")

    lines.append("")
    if trends.get("highest_spending_day"):
        lines.append(
            f"Highest spending day: {trends['highest_spending_day']['date']} "
            f"(Rs. {trends['highest_spending_day']['total']:,.2f})"
        )
    if trends.get("highest_spending_category"):
        lines.append(f"Highest spending category: {trends['highest_spending_category']}")
    if trends.get("most_frequent_category"):
        lines.append(f"Most frequent category: {trends['most_frequent_category']}")
    if trends.get("highest_spending_week"):
        lines.append(f"Highest spending week: {trends['highest_spending_week']}")

    if unusual:
        lines.append("")
        lines.append("Unusually high transactions this month:")
        for txn in unusual:
            note = f' - "{txn["note"]}"' if txn.get("note") else ""
            lines.append(
                f"- Rs. {txn['amount']:,.2f} on {txn['date']} ({txn['category']}), "
                f"{txn['times_above_average']}x the monthly average{note}"
            )

    lines.append("")
    if comparison.get("available"):
        lines.append(f"Previous month spending: Rs. {comparison['previous_total']:,.2f}")
        lines.append(f"Current month spending: Rs. {comparison['current_total']:,.2f}")
        lines.append(f"Change: {comparison['change_percent']}%")
    else:
        lines.append("Previous month data is not available.")

    return "\n".join(lines)


def _call_groq(system_prompt: str, user_prompt: str) -> str:
    """The only function that actually talks to the network. Isolated
    like this so it can be mocked out in tests."""
    if _client is None:
        raise AIServiceError(
            "GROQ_API_KEY is not set. Add it to your .env file and restart the server."
        )

    try:
        completion = _client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        raise AIServiceError(f"Groq API request failed: {e}")

    return completion.choices[0].message.content


REQUIRED_KEYS = {
    "spending_summary", "spending_patterns", "main_expense_categories",
    "recommendations", "monthly_summary",
}


def parse_ai_response(raw_content: str) -> dict:
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        raise AIServiceError("AI response was not valid JSON.")

    if not isinstance(parsed, dict):
        raise AIServiceError("AI response was not a JSON object.")

    missing = REQUIRED_KEYS - set(parsed.keys())
    if missing:
        raise AIServiceError(f"AI response missing expected fields: {sorted(missing)}")

    return parsed


def generate_ai_insights(report: dict) -> dict:
    """Full pipeline: build prompt -> call Groq -> parse response."""
    prompt = build_prompt(report)
    raw_content = _call_groq(SYSTEM_PROMPT, prompt)
    return parse_ai_response(raw_content)
