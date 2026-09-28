"""
Expense History page - lists all expenses with search/filter and delete.
"""

import streamlit as st
import pandas as pd
from services.api_client import get_expenses, delete_expense
from components.icons import icon_heading


def render():
    st.markdown(icon_heading("history", "Expense History"), unsafe_allow_html=True)

    try:
        expenses = get_expenses()
    except Exception as e:
        st.error(f"Could not load expenses. Is the FastAPI server running? ({e})")
        return

    if not expenses:
        st.info("No expenses recorded yet. Add one from the 'Add Expense' page.")
        return

    df = pd.DataFrame(expenses)
    df["expense_date"] = pd.to_datetime(df["expense_date"])
    # The API returns Decimal fields (amount) as strings to preserve precision -
    # convert to a real numeric type so formatting/math works.
    df["amount"] = pd.to_numeric(df["amount"])

    # --- Filters ---
    col1, col2 = st.columns(2)
    with col1:
        categories = ["All"] + sorted(df["category"].unique().tolist())
        selected_category = st.selectbox("Filter by category", categories)
    with col2:
        months = ["All"] + sorted(
            df["expense_date"].dt.strftime("%B %Y").unique().tolist()
        )
        selected_month = st.selectbox("Filter by month", months)

    search_term = st.text_input("Search notes", placeholder="e.g. lunch")

    filtered = df.copy()
    if selected_category != "All":
        filtered = filtered[filtered["category"] == selected_category]
    if selected_month != "All":
        filtered = filtered[
            filtered["expense_date"].dt.strftime("%B %Y") == selected_month
        ]
    if search_term:
        filtered = filtered[
            filtered["note"].fillna("").str.contains(search_term, case=False)
        ]

    filtered = filtered.sort_values("expense_date", ascending=False)

    st.write(f"Showing {len(filtered)} of {len(df)} expenses")

    # --- Table header ---
    header = st.columns([2, 2, 2, 4, 1])
    for col, label in zip(header, ["Date", "Amount", "Category", "Note", ""]):
        col.markdown(f"**{label}**")

    # --- Rows ---
    for _, row in filtered.iterrows():
        cols = st.columns([2, 2, 2, 4, 1])
        cols[0].write(row["expense_date"].strftime("%d %b %Y"))
        cols[1].write(f"₹{row['amount']:,.2f}")

        display_category = row["category"]
        if row["category"] == "Others" and row.get("custom_category"):
            display_category = row["custom_category"]
        cols[2].write(display_category)

        cols[3].write(row["note"] or "")

        if cols[4].button("🗑️", key=f"delete_{row['id']}"):
            try:
                delete_expense(int(row["id"]))
                st.rerun()
            except Exception as e:
                st.error(f"Failed to delete expense: {e}")
