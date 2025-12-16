from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.transaction import TransactionDB
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


# Create a new transaction
@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Create a new transaction for a user
    """
    # Verify user exists
    from models.user import UserDB
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Verify category exists if provided
    if transaction.category_id:
        from models.categories import CategoriesDB
        category = db.query(CategoriesDB).filter(CategoriesDB.id == transaction.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {transaction.category_id} not found"
            )

    # Create transaction
    db_transaction = TransactionDB(
        user_id=user_id,
        date=transaction.date,
        description=transaction.description,
        amount=transaction.amount,
        category_id=transaction.category_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


# Get transaction by ID
@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Get a specific transaction by ID
    """
    transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )
    return transaction


# Get all transactions for a user
@router.get("/user/{user_id}", response_model=List[TransactionOut])
def get_user_transactions(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific user with pagination
    """
    transactions = db.query(TransactionDB).filter(
        TransactionDB.user_id == user_id
    ).offset(skip).limit(limit).all()

    return transactions


# Get transactions by category
@router.get("/category/{category_id}", response_model=List[TransactionOut])
def get_transactions_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific category
    """
    transactions = db.query(TransactionDB).filter(
        TransactionDB.category_id == category_id
    ).offset(skip).limit(limit).all()

    return transactions


# Update transaction
@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a transaction
    """
    transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )

    # Update fields if provided
    if transaction_update.date is not None:
        transaction.date = transaction_update.date
    if transaction_update.description is not None:
        transaction.description = transaction_update.description
    if transaction_update.amount is not None:
        transaction.amount = transaction_update.amount
    if transaction_update.category_id is not None:
        # Verify category exists
        from models.categories import CategoriesDB
        category = db.query(CategoriesDB).filter(CategoriesDB.id == transaction_update.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {transaction_update.category_id} not found"
            )
        transaction.category_id = transaction_update.category_id

    db.commit()
    db.refresh(transaction)
    return transaction


# Delete transaction
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """
    Delete a transaction by ID
    """
    transaction = db.query(TransactionDB).filter(TransactionDB.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found"
        )

    db.delete(transaction)
    db.commit()
    return None
