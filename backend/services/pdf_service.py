"""
Generates a downloadable PDF version of the monthly report: summary
stats, category breakdown (with a bar chart), trends, unusual/duplicate
alerts, month comparison, and AI insights if already generated for
this month.

Note: uses "Rs." instead of the rupee glyph (Rs symbol) throughout,
since ReportLab's built-in fonts don't reliably include it and would
render as a broken/missing glyph.
"""

import io
from datetime import datetime
from typing import Optional
from xml.sax.saxutils import escape

import matplotlib
matplotlib.use("Agg")  # headless backend - no display needed on a server
import matplotlib.pyplot as plt

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
)

BRAND_BROWN = colors.HexColor("#3F372B")
BRAND_TAN = colors.HexColor("#A9865A")
BRAND_BEIGE = colors.HexColor("#F1E9DA")
GRID_COLOR = colors.HexColor("#EDE3CF")


def _esc(text) -> str:
    """Escape user-generated text (notes, AI output) before putting it
    in a ReportLab Paragraph, which interprets a small XML-like markup
    subset - unescaped '&', '<', '>' would otherwise break rendering."""
    if text is None:
        return ""
    return escape(str(text))


def _build_category_chart_image(category_analysis: list[dict]) -> io.BytesIO:
    categories = [c["category"] for c in category_analysis]
    amounts = [c["total"] for c in category_analysis]

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(categories, amounts, color="#A9865A")
    ax.set_ylabel("Amount (Rs.)")
    ax.set_title("Category-wise Spending")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150)
    plt.close(fig)
    buf.seek(0)
    return buf


def generate_report_pdf(report: dict, saved_insights: Optional[dict], user_name: str) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.6 * inch, bottomMargin=0.6 * inch)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleBrand", parent=styles["Title"], textColor=BRAND_BROWN)
    heading_style = ParagraphStyle("HeadingBrand", parent=styles["Heading2"], textColor=BRAND_BROWN, spaceBefore=10)
    normal_style = styles["Normal"]

    story = []

    story.append(Paragraph("Monthly Expense Report", title_style))
    story.append(Paragraph(_esc(report["month_name"]), styles["Heading3"]))
    story.append(Paragraph(
        f"Prepared for {_esc(user_name)} - Generated on {datetime.now().strftime('%d %b %Y')}",
        normal_style,
    ))
    story.append(Spacer(1, 16))

    # --- Overall summary ---
    summary = report["overall_summary"]
    story.append(Paragraph("Overall Summary", heading_style))
    summary_data = [
        ["Total Spending", f"Rs. {summary['total_spending']:,.2f}"],
        ["Transactions", str(summary["transaction_count"])],
        ["Average Transaction", f"Rs. {summary['average_transaction']:,.2f}"],
        ["Average Daily Spending", f"Rs. {summary['average_daily_spending']:,.2f}"],
    ]
    t = Table(summary_data, colWidths=[220, 200])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BRAND_BEIGE),
        ("TEXTCOLOR", (0, 0), (-1, -1), BRAND_BROWN),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 16))

    # --- Category breakdown table + chart ---
    if report["category_analysis"]:
        story.append(Paragraph("Category Analysis", heading_style))
        cat_data = [["Category", "Amount", "% of Total"]]
        for c in report["category_analysis"]:
            cat_data.append([_esc(c["category"]), f"Rs. {c['total']:,.2f}", f"{c['percentage']}%"])
        t2 = Table(cat_data, colWidths=[180, 140, 100])
        t2.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BRAND_TAN),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, GRID_COLOR),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BRAND_BEIGE]),
        ]))
        story.append(t2)
        story.append(Spacer(1, 12))

        chart_buf = _build_category_chart_image(report["category_analysis"])
        story.append(Image(chart_buf, width=5.5 * inch, height=2.75 * inch))
        story.append(Spacer(1, 16))

    # --- Trends ---
    trends = report["trends"]
    story.append(Paragraph("Spending Trends", heading_style))
    if trends.get("highest_spending_category"):
        story.append(Paragraph(f"- Highest spending category: {_esc(trends['highest_spending_category'])}", normal_style))
    if trends.get("most_frequent_category"):
        story.append(Paragraph(f"- Most frequent category: {_esc(trends['most_frequent_category'])}", normal_style))
    if trends.get("highest_spending_day"):
        d = trends["highest_spending_day"]
        story.append(Paragraph(f"- Highest spending day: {_esc(d['date'])} (Rs. {d['total']:,.2f})", normal_style))
    if trends.get("lowest_spending_day"):
        d = trends["lowest_spending_day"]
        story.append(Paragraph(f"- Lowest spending day: {_esc(d['date'])} (Rs. {d['total']:,.2f})", normal_style))
    if trends.get("highest_spending_week"):
        story.append(Paragraph(f"- Highest spending week: {_esc(trends['highest_spending_week'])}", normal_style))
    story.append(Spacer(1, 12))

    # --- Unusual transactions ---
    if report.get("unusual_transactions"):
        story.append(Paragraph("Unusually High Transactions", heading_style))
        for txn in report["unusual_transactions"]:
            note = f' - "{_esc(txn["note"])}"' if txn.get("note") else ""
            story.append(Paragraph(
                f"- Rs. {txn['amount']:,.2f} on {_esc(txn['date'])} ({_esc(txn['category'])}), "
                f"{txn['times_above_average']}x monthly average{note}",
                normal_style,
            ))
        story.append(Spacer(1, 12))

    # --- Potential duplicates ---
    if report.get("potential_duplicates"):
        story.append(Paragraph("Possible Duplicate Charges", heading_style))
        for grp in report["potential_duplicates"]:
            story.append(Paragraph(
                f"- {grp['count']}x Rs. {grp['amount']:,.2f} in {_esc(grp['category'])} on {_esc(grp['date'])}",
                normal_style,
            ))
        story.append(Spacer(1, 12))

    # --- Month comparison ---
    comparison = report.get("previous_month_comparison", {})
    story.append(Paragraph("Month-to-Month Comparison", heading_style))
    if comparison.get("available"):
        change_pct = f"{comparison['change_percent']}%" if comparison.get("change_percent") is not None else "N/A"
        story.append(Paragraph(
            f"Previous month: Rs. {comparison['previous_total']:,.2f} | "
            f"Current month: Rs. {comparison['current_total']:,.2f} | "
            f"Change: Rs. {comparison['change_amount']:,.2f} ({change_pct})",
            normal_style,
        ))
    else:
        story.append(Paragraph(_esc(comparison.get("message", "Previous month data is not available.")), normal_style))
    story.append(Spacer(1, 16))

    # --- AI insights (only if already generated for this month) ---
    story.append(Paragraph("AI Monthly Insights", heading_style))
    if saved_insights:
        story.append(Paragraph(f"<b>Summary:</b> {_esc(saved_insights.get('spending_summary', ''))}", normal_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<b>Patterns:</b> {_esc(saved_insights.get('spending_patterns', ''))}", normal_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"<b>Main Expense Categories:</b> {_esc(saved_insights.get('main_expense_categories', ''))}", normal_style
        ))
        story.append(Spacer(1, 6))
        if saved_insights.get("recommendations"):
            story.append(Paragraph("<b>Recommendations:</b>", normal_style))
            for rec in saved_insights["recommendations"]:
                story.append(Paragraph(f"- {_esc(rec)}", normal_style))
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"<i>{_esc(saved_insights.get('monthly_summary', ''))}</i>", normal_style))
    else:
        story.append(Paragraph(
            "AI insights have not been generated for this month yet. Visit the Monthly "
            "Report page and click &quot;Generate AI Insights&quot; to include them in "
            "future PDF exports.",
            normal_style,
        ))

    doc.build(story)
    buffer.seek(0)
    return buffer
