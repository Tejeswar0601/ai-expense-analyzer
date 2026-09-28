"""
Reusable widget: renders potential-duplicate-charge alerts with a
one-click "remove this entry" button per duplicate, so the user can
clean up an accidental double-submit right from the alert.
"""

import streamlit as st
from services.api_client import delete_expense


def render_duplicate_alerts(duplicates: list[dict], key_prefix: str):
    if not duplicates:
        return

    st.subheader("🔁 Possible Duplicate Charges")

    for i, group in enumerate(duplicates):
        note_list = ", ".join(f'"{n}"' for n in group["notes"] if n) or "no notes"
        confidence = (
            "Likely an accidental double-entry"
            if group["likely_double_entry"]
            else "Same amount and category on the same day - please review"
        )

        with st.container():
            st.warning(
                f"**{group['count']}x ₹{group['amount']:,.0f}** in **{group['category']}** "
                f"on {group['date']} ({note_list}). {confidence}"
            )
            btn_cols = st.columns(len(group["expense_ids"]))
            for j, expense_id in enumerate(group["expense_ids"]):
                if btn_cols[j].button(
                    f"Delete entry #{expense_id}",
                    key=f"{key_prefix}_dup_{i}_{expense_id}",
                ):
                    try:
                        delete_expense(expense_id)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not delete expense #{expense_id}: {e}")
