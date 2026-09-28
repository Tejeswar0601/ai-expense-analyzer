"""
API routes for expenses.

These functions are intentionally thin - they handle HTTP concerns
(status codes, request/response shape) and delegate real work to
the service layer. Every route now requires a valid login (via
get_current_user) and scopes all data to that user.
"""

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.models.user import User
from backend.api.deps import get_current_user
from backend.schemas.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseOut, CategorySuggestionRequest
from backend.services import expense_service, upload_service, ml_service, ocr_service

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])


@router.post("", response_model=ExpenseOut, status_code=status.HTTP_201_CREATED)
def add_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expense_service.create_expense(db, expense, current_user.id)


@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return expense_service.get_expenses(db, current_user.id, skip=skip, limit=limit)


@router.get("/{expense_id}", response_model=ExpenseOut)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = expense_service.get_expense(db, expense_id, current_user.id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated = expense_service.update_expense(db, expense_id, expense, current_user.id)
    if updated is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = expense_service.delete_expense(db, expense_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None


@router.post("/upload")
async def upload_expenses(
    file: UploadFile = File(...),
    dry_run: bool = Query(
        True,
        description="If true, only validate and return a preview - nothing is inserted.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_bytes = await file.read()

    try:
        df = upload_service.read_uploaded_file(file_bytes, file.filename)
        valid_rows, error_rows = upload_service.validate_and_clean(df)
    except upload_service.UploadValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    inserted_count = 0
    if not dry_run and valid_rows:
        for row in valid_rows:
            expense_data = ExpenseCreate(**row)
            expense_service.create_expense(db, expense_data, current_user.id)
            inserted_count += 1

    return {
        "total_rows": len(valid_rows) + len(error_rows),
        "valid_count": len(valid_rows),
        "error_count": len(error_rows),
        "inserted_count": inserted_count,
        "valid_preview": valid_rows[:50],
        "errors": error_rows[:50],
    }


@router.post("/suggest-category")
def suggest_category(
    payload: CategorySuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Suggests a category based on the note text, learned from THIS
    user's own past expenses. Never inserts or changes anything -
    purely advisory, the frontend decides whether to apply it.
    """
    return ml_service.suggest_category(db, current_user.id, payload.note)


@router.post("/scan-receipt")
async def scan_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Runs OCR on an uploaded receipt image and returns the raw text plus
    best-guess amount/date/vendor. Never inserts an expense - purely
    advisory, same as suggest-category.
    """
    file_bytes = await file.read()
    try:
        return ocr_service.parse_receipt(file_bytes)
    except ocr_service.OCRError as e:
        raise HTTPException(status_code=400, detail=str(e))
