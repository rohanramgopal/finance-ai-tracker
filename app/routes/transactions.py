from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Transaction
from app.schemas import TransactionCreate, TransactionUpdate
from app.services import normalize_category, rule_based_category

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("")
def get_transactions(db: Session = Depends(get_db)):
    rows = db.query(Transaction).order_by(Transaction.id.asc()).all()
    return [
        {
            "id": row.id,
            "date": row.date,
            "type": row.type,
            "category": row.category,
            "amount": row.amount,
            "description": row.description,
            "payment_mode": row.payment_mode,
        }
        for row in rows
    ]


@router.post("")
def add_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    category = tx.category.strip() if tx.category and tx.category.strip() else rule_based_category(tx.description, tx.type)
    category = normalize_category(category, tx.type)

    row = Transaction(
        date=tx.date,
        type=tx.type,
        category=category,
        amount=float(tx.amount),
        description=tx.description.strip(),
        payment_mode=tx.payment_mode.strip(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "message": "Transaction saved successfully",
        "saved_category": row.category,
        "id": row.id,
    }


@router.put("/{transaction_id}")
def update_transaction(transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)):
    row = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if payload.date is not None:
        row.date = payload.date
    if payload.type is not None:
        row.type = payload.type
    if payload.amount is not None:
        row.amount = float(payload.amount)
    if payload.description is not None:
        row.description = payload.description.strip()
    if payload.payment_mode is not None:
        row.payment_mode = payload.payment_mode.strip()

    if payload.category is not None and payload.category.strip():
        row.category = normalize_category(payload.category, row.type)
    else:
        row.category = normalize_category(rule_based_category(row.description, row.type), row.type)

    db.commit()
    db.refresh(row)

    return {"message": "Transaction updated successfully"}


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    row = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(row)
    db.commit()
    return {"message": "Transaction deleted successfully"}
