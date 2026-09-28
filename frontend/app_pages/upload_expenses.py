"""
Upload Expenses page - upload a CSV/XLSX, preview validated rows and
errors, then confirm to import into MySQL.
"""

import streamlit as st
import pandas as pd
from services.api_client import upload_expenses
from components.icons import icon_heading


def render():
    st.markdown(icon_heading("upload", "Upload Expenses"), unsafe_allow_html=True)
    st.write(
        "Upload a CSV or Excel file with columns: **Date, Amount, Category** "
        "(Note is optional)."
    )

    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx"])

    if uploaded_file is None:
        # Clear any stale preview from a previous upload
        st.session_state.pop("upload_preview", None)
        return

    file_bytes = uploaded_file.getvalue()
    filename = uploaded_file.name

    if st.button("Preview"):
        try:
            result = upload_expenses(file_bytes, filename, dry_run=True)
            st.session_state["upload_preview"] = result
            st.session_state["upload_file_bytes"] = file_bytes
            st.session_state["upload_filename"] = filename
        except Exception as e:
            st.error(f"Could not process file: {e}")
            return

    result = st.session_state.get("upload_preview")
    if not result:
        return

    st.subheader("Preview")
    st.write(
        f"Total rows: **{result['total_rows']}**  |  "
        f"✅ Valid: **{result['valid_count']}**  |  "
        f"❌ Errors: **{result['error_count']}**"
    )

    if result["valid_preview"]:
        st.write("Rows ready to import:")
        st.dataframe(pd.DataFrame(result["valid_preview"]), use_container_width=True)

    if result["errors"]:
        st.write("⚠️ Rows with problems (these will **not** be imported):")
        st.dataframe(pd.DataFrame(result["errors"]), use_container_width=True)

    if result["valid_count"] > 0:
        if st.button("Confirm Import"):
            try:
                final_result = upload_expenses(
                    st.session_state["upload_file_bytes"],
                    st.session_state["upload_filename"],
                    dry_run=False,
                )
                st.success(
                    f"✅ Imported {final_result['inserted_count']} expenses successfully!"
                )
                st.session_state.pop("upload_preview", None)
            except Exception as e:
                st.error(f"Import failed: {e}")
    else:
        st.warning("No valid rows to import. Fix the errors above and re-upload.")
