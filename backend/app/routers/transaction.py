from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.transaction import TransactionDB
from models.user import UserDB
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from utils.auth import get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


# Create a new transaction
@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new transaction for the authenticated user
    """
    # Verify category exists if provided and belongs to user
    if transaction.category_id:
        from models.categories import CategoriesDB
        category = db.query(CategoriesDB).filter(
            CategoriesDB.id == transaction.category_id,
            CategoriesDB.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {transaction.category_id} not found or doesn't belong to you"
            )

    # Create transaction for the authenticated user
    db_transaction = TransactionDB(
        user_id=current_user.id,
        date=transaction.date,
        description=transaction.description,
        amount=transaction.amount,
        category_id=transaction.category_id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


# Get all transactions for current user
@router.get("/", response_model=List[TransactionOut])
def get_my_transactions(
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all transactions for the authenticated user with pagination
    """
    transactions = db.query(TransactionDB).filter(
        TransactionDB.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return transactions


# Get transaction by ID (only if it belongs to user)
@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific transaction by ID (must belong to authenticated user)
    """
    transaction = db.query(TransactionDB).filter(
        TransactionDB.id == transaction_id,
        TransactionDB.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found or doesn't belong to you"
        )
    return transaction


# Get transactions by category
@router.get("/category/{category_id}", response_model=List[TransactionOut])
def get_transactions_by_category(
    category_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all transactions for a specific category (must belong to user)
    """
    transactions = db.query(TransactionDB).filter(
        TransactionDB.category_id == category_id,
        TransactionDB.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return transactions


# Update transaction
@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a transaction (must belong to user)
    """
    transaction = db.query(TransactionDB).filter(
        TransactionDB.id == transaction_id,
        TransactionDB.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found or doesn't belong to you"
        )

    # Update fields if provided
    if transaction_update.date is not None:
        transaction.date = transaction_update.date
    if transaction_update.description is not None:
        transaction.description = transaction_update.description
    if transaction_update.amount is not None:
        transaction.amount = transaction_update.amount
    if transaction_update.category_id is not None:
        # Verify category exists and belongs to user
        from models.categories import CategoriesDB
        category = db.query(CategoriesDB).filter(
            CategoriesDB.id == transaction_update.category_id,
            CategoriesDB.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {transaction_update.category_id} not found or doesn't belong to you"
            )
        transaction.category_id = transaction_update.category_id

    db.commit()
    db.refresh(transaction)
    return transaction


# Delete transaction
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a transaction by ID (must belong to user)
    """
    transaction = db.query(TransactionDB).filter(
        TransactionDB.id == transaction_id,
        TransactionDB.user_id == current_user.id
    ).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found or doesn't belong to you"
        )

    db.delete(transaction)
    db.commit()
    return None
