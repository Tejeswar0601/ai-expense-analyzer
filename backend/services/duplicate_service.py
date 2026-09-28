"""
Duplicate-charge detection: flags expenses that look like the same
charge entered more than once.

Data-model note: expense_date is stored as a DATE only (no time-of-day),
matching how expenses are actually entered. So "duplicate" here means
same category, same amount, same calendar day. We additionally check
created_at (when the row was saved to the database) - if two matching
rows were also created within a few minutes of each other, that's a
strong signal of an accidental double-submit, flagged separately as
"likely_double_entry" rather than just a coincidental same-day/same-
amount purchase (e.g. two separate ₹150 coffees).
"""

from datetime import timedelta

import pandas as pd

DOUBLE_ENTRY_WINDOW_MINUTES = 10


def detect_duplicate_charges(df: pd.DataFrame) -> list[dict]:
    """
    Pure function: given a prepared expenses dataframe (must include
    display_category, amount, expense_date, created_at, id, note),
    find groups of same category + amount + calendar day.
    """
    if df.empty or len(df) < 2 or "created_at" not in df.columns:
        return []

    groups = []
    grouped = df.groupby(["display_category", "amount", df["expense_date"].dt.date])

    for (category, amount, day), group in grouped:
        if len(group) < 2:
            continue

        created_times = sorted(group["created_at"].tolist())
        likely_double_entry = any(
            created_times[i] - created_times[i - 1] <= timedelta(minutes=DOUBLE_ENTRY_WINDOW_MINUTES)
            for i in range(1, len(created_times))
        )

        groups.append({
            "category": category,
            "amount": round(float(amount), 2),
            "date": str(day),
            "count": int(len(group)),
            "expense_ids": [int(x) for x in group["id"].tolist()],
            "notes": [n if pd.notna(n) else None for n in group["note"].tolist()],
            "likely_double_entry": likely_double_entry,
        })

    # Show the most confident (likely double-entry) and highest-amount groups first
    groups.sort(key=lambda g: (not g["likely_double_entry"], -g["amount"]))
    return groups
