from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.budgets import BudgetsDB
from schemas.budget import BudgetCreate, BudgetUpdate, BudgetOut

router = APIRouter(
    prefix="/budgets",
    tags=["budgets"]
)


# Create a new budget
@router.post("/", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(budget: BudgetCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Create a new budget for a user
    """
    # Verify user exists
    from models.user import UserDB
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Create budget
    db_budget = BudgetsDB(
        user_id=user_id,
        name=budget.name,
        start_date=budget.start_date,
        end_date=budget.end_date
    )
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)

    return db_budget


# Get budget by ID
@router.get("/{budget_id}", response_model=BudgetOut)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    """
    Get a specific budget by ID
    """
    budget = db.query(BudgetsDB).filter(BudgetsDB.id == budget_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with id {budget_id} not found"
        )
    return budget


# Get all budgets for a user
@router.get("/user/{user_id}", response_model=List[BudgetOut])
def get_user_budgets(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all budgets for a specific user with pagination
    """
    budgets = db.query(BudgetsDB).filter(
        BudgetsDB.user_id == user_id
    ).offset(skip).limit(limit).all()

    return budgets


# Get active budgets for a user (current date is between start_date and end_date)
@router.get("/user/{user_id}/active", response_model=List[BudgetOut])
def get_active_budgets(user_id: int, db: Session = Depends(get_db)):
    """
    Get all active budgets for a specific user
    """
    from datetime import date
    from sqlalchemy import and_

    today = date.today()
    budgets = db.query(BudgetsDB).filter(
        and_(
            BudgetsDB.user_id == user_id,
            BudgetsDB.start_date <= today,
            BudgetsDB.end_date >= today
        )
    ).all()

    return budgets


# Update budget
@router.put("/{budget_id}", response_model=BudgetOut)
def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a budget
    """
    budget = db.query(BudgetsDB).filter(BudgetsDB.id == budget_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with id {budget_id} not found"
        )

    # Update fields if provided
    if budget_update.name is not None:
        budget.name = budget_update.name
    if budget_update.start_date is not None:
        budget.start_date = budget_update.start_date
    if budget_update.end_date is not None:
        budget.end_date = budget_update.end_date

    # Validate dates
    if budget.start_date > budget.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date cannot be after end date"
        )

    db.commit()
    db.refresh(budget)
    return budget


# Delete budget
@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    """
    Delete a budget by ID
    """
    budget = db.query(BudgetsDB).filter(BudgetsDB.id == budget_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Budget with id {budget_id} not found"
        )

    db.delete(budget)
    db.commit()
    return None
