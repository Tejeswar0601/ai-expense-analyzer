"""
Monthly Report page - the full report: statistics, charts, category
breakdown, month comparison, and (on request) AI-generated insights.
"""

import calendar
from datetime import date

import pandas as pd
import streamlit as st

from services.api_client import get_monthly_report, generate_ai_report, get_saved_insights, download_report_pdf
from components.icons import icon_heading
from components.duplicate_alerts import render_duplicate_alerts
from components.charts import (
    category_bar_chart,
    category_pie_chart,
    daily_spending_line_chart,
    weekly_spending_bar_chart,
)


def _month_options(months_back: int = 12) -> list[tuple[str, int, int]]:
    today = date.today()
    options = []
    year, month = today.year, today.month
    for _ in range(months_back):
        label = f"{calendar.month_name[month]} {year}"
        options.append((label, year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return options


def _render_summary(report: dict):
    summary = report["overall_summary"]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Spending", f"₹{summary['total_spending']:,.0f}")
    col2.metric("Transactions", summary["transaction_count"])
    col3.metric("Average Transaction", f"₹{summary['average_transaction']:,.0f}")
    col4.metric("Average Daily Spending", f"₹{summary['average_daily_spending']:,.0f}")


def _render_charts(report: dict):
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(category_bar_chart(report["category_analysis"]), use_container_width=True)
    with chart_col2:
        st.plotly_chart(category_pie_chart(report["category_analysis"]), use_container_width=True)

    st.plotly_chart(daily_spending_line_chart(report["daily_totals"]), use_container_width=True)
    st.plotly_chart(weekly_spending_bar_chart(report["weekly_totals"]), use_container_width=True)


def _render_category_table(report: dict):
    st.subheader("Category Analysis")
    df = pd.DataFrame(report["category_analysis"])
    df = df.rename(columns={"category": "Category", "total": "Amount (₹)", "percentage": "% of Total"})
    st.dataframe(df, use_container_width=True, hide_index=True)


def _render_trends(report: dict):
    st.subheader("Spending Trends")
    trends = report["trends"]
    t1, t2, t3 = st.columns(3)
    t1.write(f"**Highest spending category:** {trends['highest_spending_category']}")
    t1.write(f"**Most frequent category:** {trends['most_frequent_category']}")
    if trends["highest_spending_day"]:
        t2.write(
            f"**Highest spending day:** {trends['highest_spending_day']['date']} "
            f"(₹{trends['highest_spending_day']['total']:,.0f})"
        )
    if trends["lowest_spending_day"]:
        t2.write(
            f"**Lowest spending day:** {trends['lowest_spending_day']['date']} "
            f"(₹{trends['lowest_spending_day']['total']:,.0f})"
        )
    t3.write(f"**Highest spending week:** {trends['highest_spending_week']}")

    if report["unusual_transactions"]:
        st.write("**Unusually high transactions:**")
        for txn in report["unusual_transactions"]:
            note = f" — \"{txn['note']}\"" if txn.get("note") else ""
            st.warning(
                f"₹{txn['amount']:,.0f} on {txn['date']} ({txn['category']}), "
                f"{txn['times_above_average']}x your monthly average{note}"
            )


def _render_comparison(report: dict):
    st.subheader("Month-to-Month Comparison")
    comparison = report["previous_month_comparison"]

    if not comparison["available"]:
        st.info(comparison["message"])
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Previous Month", f"₹{comparison['previous_total']:,.0f}")
    c2.metric("Current Month", f"₹{comparison['current_total']:,.0f}")
    change_label = f"{comparison['change_percent']}%" if comparison["change_percent"] is not None else "N/A"
    c3.metric("Change", f"₹{comparison['change_amount']:,.0f}", change_label)

    if comparison["top_contributing_categories"]:
        st.write("**Categories that changed the most:**")
        for cat in comparison["top_contributing_categories"]:
            direction = "up" if cat["change"] > 0 else "down"
            st.write(
                f"- {cat['category']}: ₹{cat['previous']:,.0f} → ₹{cat['current']:,.0f} "
                f"({direction} ₹{abs(cat['change']):,.0f})"
            )


def _render_ai_section(year: int, month: int):
    st.markdown(icon_heading("ai_insights", "AI Monthly Insights", tag="h3"), unsafe_allow_html=True)

    # On first render for this month, try loading previously saved
    # insights (no Groq call) instead of always starting from scratch.
    if st.session_state.get("ai_report_month") != (year, month):
        st.session_state.pop("ai_report", None)
        try:
            saved = get_saved_insights(year, month)
            if saved:
                st.session_state["ai_report"] = {
                    "ai_status": "success",
                    "ai_insights": saved,
                    "from_saved": True,
                }
        except Exception:
            pass  # if this fails, just fall through to the normal "generate" flow
        st.session_state["ai_report_month"] = (year, month)

    has_existing = st.session_state.get("ai_report") is not None
    button_label = "Regenerate AI Insights" if has_existing else "Generate AI Insights"

    if st.button(button_label):
        with st.spinner("Asking the AI to analyze your spending..."):
            try:
                fresh = generate_ai_report(year, month)
                fresh["from_saved"] = False
                st.session_state["ai_report"] = fresh
            except Exception as e:
                st.error(f"Could not reach the server: {e}")
                return

    result = st.session_state.get("ai_report")
    if not result:
        st.caption("Click the button above to generate AI-powered insights for this month.")
        return

    if result.get("ai_status") != "success" or not result.get("ai_insights"):
        st.warning(
            "AI insights could not be generated right now, but your statistics above "
            "are still accurate. "
            f"(Reason: {result.get('ai_error', 'unknown error')})"
        )
        return

    if result.get("from_saved"):
        st.caption("📁 Showing previously generated insights for this month.")

    insights = result["ai_insights"]
    st.write(f"**Summary:** {insights['spending_summary']}")
    st.write(f"**Patterns:** {insights['spending_patterns']}")
    st.write(f"**Main Expense Categories:** {insights['main_expense_categories']}")

    st.write("**💡 Recommendations:**")
    for rec in insights["recommendations"]:
        st.write(f"- {rec}")

    st.success(insights["monthly_summary"])


def render():
    st.markdown(icon_heading("report", "Monthly Report"), unsafe_allow_html=True)

    options = _month_options()
    labels = [o[0] for o in options]
    selected_label = st.selectbox("Select Month", labels)
    _, year, month = next(o for o in options if o[0] == selected_label)

    # Reset cached AI insights if the user switches months
    if st.session_state.get("ai_report_month") != (year, month):
        st.session_state.pop("ai_report", None)
        st.session_state["ai_report_month"] = (year, month)

    try:
        report = get_monthly_report(year, month)
    except Exception as e:
        st.error(f"Could not load report. Is the FastAPI server running? ({e})")
        return

    if report["overall_summary"]["transaction_count"] == 0:
        st.info(f"No expenses recorded for {selected_label} yet.")
        return

    # --- PDF export ---
    pdf_col1, pdf_col2 = st.columns([1, 3])
    with pdf_col1:
        if st.button("📄 Prepare PDF"):
            with st.spinner("Building your PDF report..."):
                try:
                    st.session_state["pdf_bytes"] = download_report_pdf(year, month)
                    st.session_state["pdf_month"] = (year, month)
                except Exception as e:
                    st.error(f"Could not generate PDF: {e}")

    if st.session_state.get("pdf_bytes") and st.session_state.get("pdf_month") == (year, month):
        with pdf_col2:
            st.download_button(
                "⬇️ Download PDF Report",
                data=st.session_state["pdf_bytes"],
                file_name=f"expense_report_{year:04d}-{month:02d}.pdf",
                mime="application/pdf",
            )

    st.divider()

    _render_summary(report)
    st.divider()
    _render_charts(report)
    st.divider()
    _render_category_table(report)
    st.divider()
    _render_trends(report)
    st.divider()
    render_duplicate_alerts(report.get("potential_duplicates", []), key_prefix="monthly_report")
    st.divider()
    _render_comparison(report)
    st.divider()
    _render_ai_section(year, month)
