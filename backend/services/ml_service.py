"""
ML-based category suggestion: trains a small TF-IDF + Naive Bayes
classifier on THIS USER's own past expense notes, to suggest a
category when they type a note for a new expense.

Trained fresh on each request rather than cached - personal expense
histories are small, so retraining is fast and avoids stale-model
bugs after the user adds/edits/deletes expenses. Each user's model
is trained ONLY on their own data, consistent with the rest of the
app's data isolation (see Phase 13).

This is a SUGGESTION only - the API never inserts or changes a
category itself. The frontend shows it as an optional hint the
person can apply or ignore.
"""

from typing import Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sqlalchemy.orm import Session

from backend.models.expense import Expense

MIN_TRAINING_EXAMPLES = 8
MIN_DISTINCT_CATEGORIES = 2


def _get_training_data(db: Session, user_id: int) -> tuple[list[str], list[str]]:
    """This user's past expenses that have a non-empty note. Uses the
    display category (custom_category for 'Others' rows) as the label,
    so a suggestion can point straight at a custom category like
    'Gym Equipment' rather than just generic 'Others'."""
    rows = (
        db.query(Expense)
        .filter(Expense.user_id == user_id, Expense.note.isnot(None), Expense.note != "")
        .all()
    )

    notes, labels = [], []
    for r in rows:
        label = r.custom_category if (r.category == "Others" and r.custom_category) else r.category
        notes.append(r.note)
        labels.append(label)

    return notes, labels


def suggest_category(db: Session, user_id: int, note: str) -> dict:
    note = (note or "").strip()
    if not note:
        return {"available": False, "message": "Type a note to get a category suggestion."}

    notes, labels = _get_training_data(db, user_id)

    if len(notes) < MIN_TRAINING_EXAMPLES or len(set(labels)) < MIN_DISTINCT_CATEGORIES:
        return {
            "available": False,
            "message": (
                f"Not enough expense history yet to suggest categories - add at least "
                f"{MIN_TRAINING_EXAMPLES} expenses with notes, across at least "
                f"{MIN_DISTINCT_CATEGORIES} categories, and this will kick in."
            ),
        }

    try:
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", min_df=1, ngram_range=(1, 2))),
            # fit_prior=False: treat every category as equally likely up front,
            # so a category you've logged more often doesn't get an unfair
            # head start over one with fewer but more distinctive examples.
            ("nb", MultinomialNB(fit_prior=False)),
        ])
        pipeline.fit(notes, labels)

        raw_prediction = pipeline.predict([note])[0]
        predicted = str(raw_prediction)
        probabilities = pipeline.predict_proba([note])[0]
        class_index = list(pipeline.classes_).index(raw_prediction)
        confidence = round(float(probabilities[class_index]), 2)
    except Exception:
        return {"available": False, "message": "Could not generate a suggestion this time."}

    return {
        "available": True,
        "suggested_category": predicted,
        "confidence": confidence,
        "trained_on_examples": len(notes),
    }
