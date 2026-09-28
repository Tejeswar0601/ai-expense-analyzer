"""
Add Expense page - a form that posts a new expense to the FastAPI backend.

Two optional AI-assisted helpers, both purely advisory (never auto-save):
1. Scan a receipt photo (OCR) to guess amount/date/vendor
2. Type a note to get an ML category suggestion, learned from your own history
"""

from datetime import date
import streamlit as st
from services.api_client import add_expense, suggest_category, scan_receipt
from components.icons import icon_heading

CATEGORIES = [
    "Food", "Travel", "Shopping", "Bills", "Health",
    "Entertainment", "Education", "Subscriptions", "Rent", "Others",
]


def render():
    st.markdown(icon_heading("add_expense", "Add Daily Expense"), unsafe_allow_html=True)

    # --- Apply any pending OCR-scanned values BEFORE creating widgets
    # this run (Streamlit only lets you set a widget's session_state
    # value before that widget is instantiated in the same script run).
    pending = st.session_state.pop("ocr_apply_pending", None)
    if pending:
        if pending.get("note"):
            st.session_state["expense_note"] = pending["note"]
        if pending.get("date"):
            try:
                st.session_state["expense_date_input"] = date.fromisoformat(pending["date"])
            except ValueError:
                pass
        if pending.get("amount") is not None:
            st.session_state["expense_amount_input"] = float(pending["amount"])

    # --- Receipt scan (optional) ---
    with st.expander("📷 Scan a receipt (optional)"):
        receipt_file = st.file_uploader(
            "Upload a receipt photo", type=["jpg", "jpeg", "png"], key="receipt_uploader"
        )
        if receipt_file is not None and st.button("Scan Receipt"):
            with st.spinner("Reading receipt..."):
                try:
                    st.session_state["ocr_result"] = scan_receipt(
                        receipt_file.getvalue(), receipt_file.name
                    )
                except Exception as e:
                    st.error(f"Could not scan receipt: {e}")

        ocr_result = st.session_state.get("ocr_result")
        if ocr_result:
            if ocr_result.get("available"):
                st.text_area(
                    "Extracted text (review this against the actual receipt)",
                    value=ocr_result["raw_text"],
                    height=100,
                    disabled=True,
                )
                c1, c2, c3 = st.columns(3)
                amt = ocr_result.get("suggested_amount")
                c1.write(f"**Amount:** {'₹' + format(amt, ',.2f') if amt else 'Not detected'}")
                c2.write(f"**Date:** {ocr_result.get('suggested_date') or 'Not detected'}")
                c3.write(f"**Vendor:** {ocr_result.get('suggested_note') or 'Not detected'}")
                st.caption("OCR isn't perfect - double-check these against the real receipt before saving.")
                if st.button("Apply to form below"):
                    st.session_state["ocr_apply_pending"] = {
                        "note": ocr_result.get("suggested_note"),
                        "date": ocr_result.get("suggested_date"),
                        "amount": ocr_result.get("suggested_amount"),
                    }
                    st.rerun()
            else:
                st.warning(ocr_result.get("message", "Could not read this receipt."))

    st.divider()

    # --- Note + ML category suggestion ---
    st.caption(
        "Type a note below for an optional AI category suggestion, "
        "based on your own past expenses - or just fill out the form directly."
    )
    note = st.text_input("Note", placeholder="e.g. Uber ride to airport", key="expense_note")

    if st.button("💡 Suggest Category", disabled=not note.strip()):
        try:
            st.session_state["ml_suggestion"] = suggest_category(note)
        except Exception as e:
            st.error(f"Could not get a suggestion: {e}")

    suggestion = st.session_state.get("ml_suggestion")
    if suggestion:
        if suggestion.get("available"):
            st.info(
                f"💡 Suggested category: **{suggestion['suggested_category']}** "
                f"({suggestion['confidence'] * 100:.0f}% confidence, based on "
                f"{suggestion['trained_on_examples']} of your past expenses)"
            )
            if st.button("Apply Suggestion"):
                suggested = suggestion["suggested_category"]
                if suggested in CATEGORIES:
                    st.session_state["applied_category"] = suggested
                    st.session_state["applied_custom"] = ""
                else:
                    st.session_state["applied_category"] = "Others"
                    st.session_state["applied_custom"] = suggested
        else:
            st.caption(suggestion.get("message", ""))

    applied_category = st.session_state.get("applied_category")
    default_index = CATEGORIES.index(applied_category) if applied_category in CATEGORIES else 0

    st.divider()

    with st.form("add_expense_form", clear_on_submit=True):
        expense_date = st.date_input("Date", value=date.today(), key="expense_date_input")
        amount = st.number_input(
            "Amount (₹)", min_value=0.0, step=1.0, format="%.2f", key="expense_amount_input"
        )
        category = st.selectbox("Category", CATEGORIES, index=default_index)

        custom_category = None
        if category == "Others":
            custom_category = st.text_input(
                "Enter category type",
                value=st.session_state.get("applied_custom", ""),
                placeholder="e.g. Gym Equipment",
            )

        submitted = st.form_submit_button("Add Expense")

    if not submitted:
        return

    if amount <= 0:
        st.error("Amount must be greater than zero.")
        return

    payload = {
        "expense_date": expense_date.isoformat(),
        "amount": float(amount),
        "category": category,
        "custom_category": custom_category if custom_category else None,
        "note": note if note else None,
    }

    try:
        add_expense(payload)
        st.success("✅ Expense added successfully!")
        for key in ["ml_suggestion", "applied_category", "applied_custom", "ocr_result"]:
            st.session_state.pop(key, None)
        st.rerun()
    except Exception as e:
        st.error(f"Failed to add expense. Is the FastAPI server running? ({e})")
