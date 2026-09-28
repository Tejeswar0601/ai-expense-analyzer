"""
Budgets page - set a monthly spending cap per category, and see how
much of it has been used so far this month.
"""

import calendar
from datetime import date

import streamlit as st

from services.api_client import set_budget, get_budget_utilization, delete_budget
from components.icons import icon_heading

CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills", "Health",
    "Entertainment", "Education", "Subscriptions", "Rent", "Others",
]

STATUS_LABELS = {
    "on_track": "On track",
    "near_limit": "Near limit",
    "over_budget": "Over budget",
}

STATUS_CSS_CLASS = {
    "on_track": "on-track",
    "near_limit": "near-limit",
    "over_budget": "over-budget",
}


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


def _render_bar(row: dict):
    css_class = STATUS_CSS_CLASS[row["status"]]
    fill_percent = min(row["percent_used"], 100)  # visually cap the bar at 100%
    st.markdown(
        f'''<div style="margin-bottom:1rem;">
            <div style="display:flex; justify-content:space-between; font-weight:600; color:#3F372B;">
                <span>{row["category"]}</span>
                <span>₹{row["spent"]:,.0f} / ₹{row["monthly_limit"]:,.0f} ({row["percent_used"]:.0f}%)</span>
            </div>
            <div class="budget-bar-track">
                <div class="budget-bar-fill {css_class}" style="width:{fill_percent}%;"></div>
            </div>
            <div style="font-size:0.85rem; color:#8A7F6E;">
                {STATUS_LABELS[row["status"]]}
                {"- ₹" + format(abs(row["remaining"]), ",.0f") + " over" if row["remaining"] < 0 else "- ₹" + format(row["remaining"], ",.0f") + " remaining"}
            </div>
        </div>''',
        unsafe_allow_html=True,
    )


def render():
    st.markdown(icon_heading("budgets", "Budgets"), unsafe_allow_html=True)
    st.caption("Set a monthly spending cap per category and track how close you are to it.")

    options = _month_options()
    labels = [o[0] for o in options]
    selected_label = st.selectbox("Month", labels)
    _, year, month = next(o for o in options if o[0] == selected_label)
    month_year = f"{year:04d}-{month:02d}"

    st.divider()

    with st.expander("Set a budget", expanded=False):
        with st.form("set_budget_form"):
            category = st.selectbox("Category", CATEGORIES)
            monthly_limit = st.number_input(
                "Monthly Limit (₹)", min_value=0.0, step=100.0, format="%.2f"
            )
            submitted = st.form_submit_button("Save Budget")

        if submitted:
            if monthly_limit <= 0:
                st.error("Budget limit must be greater than zero.")
            else:
                try:
                    set_budget(category, float(monthly_limit), month_year)
                    st.success(f"✅ Budget for {category} set to ₹{monthly_limit:,.0f} for {selected_label}.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Could not save budget: {e}")

    st.divider()

    try:
        rows = get_budget_utilization(year, month)
    except Exception as e:
        st.error(f"Could not load budgets. Is the FastAPI server running? ({e})")
        return

    if not rows:
        st.info(f"No budgets set for {selected_label} yet. Use the form above to add one.")
        return

    over_count = sum(1 for r in rows if r["status"] == "over_budget")
    near_count = sum(1 for r in rows if r["status"] == "near_limit")
    if over_count:
        st.warning(f"⚠️ {over_count} categor{'y is' if over_count == 1 else 'ies are'} over budget this month.")
    elif near_count:
        st.info(f"{near_count} categor{'y is' if near_count == 1 else 'ies are'} close to the limit.")

    for row in rows:
        _render_bar(row)
        if st.button(f"Remove {row['category']} budget", key=f"delete_budget_{row['id']}"):
            try:
                delete_budget(row["id"])
                st.rerun()
            except Exception as e:
                st.error(f"Could not remove budget: {e}")
