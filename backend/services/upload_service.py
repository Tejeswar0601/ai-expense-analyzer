"""
Upload service: reads a CSV/XLSX file, validates every row, and separates
it into rows ready to import vs. rows with problems.

Nothing here touches the database - it's pure parsing/validation logic,
reused by the API for both the "preview" and "confirm" steps.
"""

import io
from decimal import Decimal, InvalidOperation
from typing import Dict, List, Tuple

import pandas as pd

REQUIRED_COLUMNS = {"Date", "Amount", "Category"}

DEFAULT_CATEGORIES = {
    "Food", "Travel", "Shopping", "Bills", "Health",
    "Entertainment", "Education", "Subscriptions", "Rent", "Others",
}


class UploadValidationError(Exception):
    """Raised when the file itself can't be processed at all
    (wrong type, unreadable, empty, missing required columns)."""
    pass


def read_uploaded_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    """Read CSV or XLSX bytes into a DataFrame."""
    name_lower = filename.lower()

    if name_lower.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(file_bytes))
        except Exception as e:
            raise UploadValidationError(f"Could not read CSV file: {e}")
    elif name_lower.endswith(".xlsx"):
        try:
            df = pd.read_excel(io.BytesIO(file_bytes))
        except Exception as e:
            raise UploadValidationError(f"Could not read Excel file: {e}")
    else:
        raise UploadValidationError(
            "Unsupported file type. Please upload a .csv or .xlsx file."
        )

    if df.empty:
        raise UploadValidationError("The uploaded file is empty.")

    return df


def validate_and_clean(df: pd.DataFrame) -> Tuple[List[Dict], List[Dict]]:
    """
    Validate and clean every row.

    Returns:
        valid_rows: list of dicts ready to pass into ExpenseCreate
        error_rows: list of dicts describing what's wrong with each bad row
    """
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise UploadValidationError(
            f"Missing required column(s): {', '.join(sorted(missing))}. "
            f"Expected columns: Date, Amount, Category, Note (optional)."
        )

    # Drop rows that are completely empty (common in exported spreadsheets)
    df = df.dropna(how="all")

    valid_rows: List[Dict] = []
    error_rows: List[Dict] = []
    seen_keys = set()

    has_note_column = "Note" in df.columns

    for idx, row in df.iterrows():
        row_number = idx + 2  # +1 for header row, +1 to convert 0-index to 1-index
        raw_date = row.get("Date")
        raw_amount = row.get("Amount")
        raw_category = row.get("Category")
        raw_note = row.get("Note") if has_note_column else None

        errors: List[str] = []

        # --- Date ---
        parsed_date = None
        if pd.isna(raw_date):
            errors.append("Date is missing")
        else:
            try:
                parsed_date = pd.to_datetime(raw_date).date()
            except Exception:
                errors.append(f"Invalid date: '{raw_date}'")

        # --- Amount ---
        parsed_amount = None
        if pd.isna(raw_amount):
            errors.append("Amount is missing")
        else:
            try:
                parsed_amount = Decimal(str(raw_amount).strip())
                if parsed_amount <= 0:
                    errors.append("Amount must be greater than zero")
            except (InvalidOperation, ValueError):
                errors.append(f"Invalid amount: '{raw_amount}'")

        # --- Category (unknown categories are auto-mapped to Others) ---
        category = None
        custom_category = None
        if pd.isna(raw_category) or str(raw_category).strip() == "":
            errors.append("Category is missing")
        else:
            cat_str = str(raw_category).strip()
            if cat_str in DEFAULT_CATEGORIES:
                category = cat_str
            else:
                category = "Others"
                custom_category = cat_str

        # --- Note (optional) ---
        note = None
        if raw_note is not None and not pd.isna(raw_note):
            note = str(raw_note).strip()

        # --- Duplicate detection within this file ---
        if not errors:
            row_key = (parsed_date, parsed_amount, category, custom_category, note)
            if row_key in seen_keys:
                errors.append("Duplicate row within uploaded file")
            else:
                seen_keys.add(row_key)

        if errors:
            error_rows.append({
                "row_number": row_number,
                "reason": "; ".join(errors),
                "Date": "" if pd.isna(raw_date) else str(raw_date),
                "Amount": "" if pd.isna(raw_amount) else str(raw_amount),
                "Category": "" if pd.isna(raw_category) else str(raw_category),
                "Note": "" if raw_note is None or pd.isna(raw_note) else str(raw_note),
            })
        else:
            valid_rows.append({
                "expense_date": parsed_date.isoformat(),
                "amount": float(parsed_amount),
                "category": category,
                "custom_category": custom_category,
                "note": note,
            })

    return valid_rows, error_rows
