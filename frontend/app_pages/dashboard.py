"""
Dashboard page - month selector, summary cards, and Plotly charts.
"""

from datetime import date
import calendar

import streamlit as st

from services.api_client import get_monthly_report, get_forecast
from components.icons import icon_heading
from components.duplicate_alerts import render_duplicate_alerts
from components.charts import (
    category_bar_chart,
    category_pie_chart,
    daily_spending_line_chart,
    weekly_spending_bar_chart,
)


def _month_options(months_back: int = 12) -> list[tuple[str, int, int]]:
    """Build a list of (label, year, month) for the last N months, most recent first."""
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


def render():
    st.markdown(icon_heading("dashboard", "Dashboard"), unsafe_allow_html=True)

    options = _month_options()
    labels = [o[0] for o in options]
    selected_label = st.selectbox("Month", labels)
    _, year, month = next(o for o in options if o[0] == selected_label)

    try:
        report = get_monthly_report(year, month)
    except Exception as e:
        st.error(f"Could not load report. Is the FastAPI server running? ({e})")
        return

    summary = report["overall_summary"]

    if summary["transaction_count"] == 0:
        st.info(f"No expenses recorded for {selected_label} yet.")
        return

    # --- Summary cards ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Spending", f"₹{summary['total_spending']:,.0f}")
    col2.metric("Transactions", summary["transaction_count"])
    col3.metric("Average Transaction", f"₹{summary['average_transaction']:,.0f}")
    col4.metric("Average Daily Spending", f"₹{summary['average_daily_spending']:,.0f}")

    trends = report["trends"]
    col5, col6 = st.columns(2)
    col5.metric("Highest Spending Category", trends["highest_spending_category"] or "-")
    if trends["highest_spending_day"]:
        col6.metric(
            "Highest Spending Day",
            trends["highest_spending_day"]["date"],
            f"₹{trends['highest_spending_day']['total']:,.0f}",
        )

    st.divider()

    # --- Predictive forecast (only shows for the current, in-progress month) ---
    try:
        forecast = get_forecast(year, month)
    except Exception:
        forecast = {"available": False}

    if forecast.get("available"):
        st.markdown(icon_heading("forecast", "Month-End Forecast", tag="h3"), unsafe_allow_html=True)

        confidence_note = {
            "low": "Early days - this projection will firm up as the month goes on.",
            "medium": "Based on a couple weeks of data - reasonably reliable.",
            "high": "Based on most of the month's data - fairly confident.",
        }[forecast["confidence"]]

        fcol1, fcol2, fcol3 = st.columns(3)
        fcol1.metric("Spent So Far", f"₹{forecast['spent_so_far']:,.0f}")
        fcol2.metric("Projected Month-End Total", f"₹{forecast['projected_month_end_total']:,.0f}")
        fcol3.metric("Daily Average Rate", f"₹{forecast['daily_average_rate']:,.0f}/day")
        st.caption(
            f"{forecast['days_elapsed']} of {forecast['days_in_month']} days elapsed. {confidence_note}"
        )

        if forecast["category_forecast"]:
            with st.expander("Per-category projection"):
                for cat in forecast["category_forecast"]:
                    st.write(
                        f"**{cat['category']}**: ₹{cat['spent_so_far']:,.0f} so far → "
                        f"projected ₹{cat['projected_total']:,.0f} by month-end"
                    )

        st.divider()

    # --- Charts ---
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(category_bar_chart(report["category_analysis"]), use_container_width=True)
    with chart_col2:
        st.plotly_chart(category_pie_chart(report["category_analysis"]), use_container_width=True)

    st.plotly_chart(daily_spending_line_chart(report["daily_totals"]), use_container_width=True)
    st.plotly_chart(weekly_spending_bar_chart(report["weekly_totals"]), use_container_width=True)

    # --- Unusual transactions ---
    if report["unusual_transactions"]:
        st.subheader("⚠️ Unusually High Transactions")
        for txn in report["unusual_transactions"]:
            st.warning(
                f"₹{txn['amount']:,.0f} on {txn['date']} ({txn['category']}) - "
                f"{txn['times_above_average']}x your monthly average"
                + (f" — \"{txn['note']}\"" if txn["note"] else "")
            )

    # --- Possible duplicate charges ---
    render_duplicate_alerts(report.get("potential_duplicates", []), key_prefix="dashboard")
