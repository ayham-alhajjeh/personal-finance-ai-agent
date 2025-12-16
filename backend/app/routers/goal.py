from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.goals import GoalsDB
from schemas.goal import GoalsCreate, GoalsUpdate, GoalsOut

router = APIRouter(
    prefix="/goals",
    tags=["goals"]
)


# Create a new goal
@router.post("/", response_model=GoalsOut, status_code=status.HTTP_201_CREATED)
def create_goal(goal: GoalsCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Create a new goal for a user
    """
    # Verify user exists
    from models.user import UserDB
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Create goal
    db_goal = GoalsDB(
        user_id=user_id,
        name=goal.name,
        target_amount=goal.target_amount,
        target_date=goal.target_date
    )
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)

    return db_goal


# Get goal by ID
@router.get("/{goal_id}", response_model=GoalsOut)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    """
    Get a specific goal by ID
    """
    goal = db.query(GoalsDB).filter(GoalsDB.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found"
        )
    return goal


# Get all goals for a user
@router.get("/user/{user_id}", response_model=List[GoalsOut])
def get_user_goals(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all goals for a specific user with pagination
    """
    goals = db.query(GoalsDB).filter(
        GoalsDB.user_id == user_id
    ).offset(skip).limit(limit).all()

    return goals


# Get active goals (target_date is in the future)
@router.get("/user/{user_id}/active", response_model=List[GoalsOut])
def get_active_goals(user_id: int, db: Session = Depends(get_db)):
    """
    Get all active goals for a specific user (target date in future)
    """
    from datetime import date

    today = date.today()
    goals = db.query(GoalsDB).filter(
        GoalsDB.user_id == user_id,
        GoalsDB.target_date >= today
    ).all()

    return goals


# Update goal
@router.put("/{goal_id}", response_model=GoalsOut)
def update_goal(
    goal_id: int,
    goal_update: GoalsUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a goal
    """
    goal = db.query(GoalsDB).filter(GoalsDB.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found"
        )

    # Update fields if provided
    if goal_update.name is not None:
        goal.name = goal_update.name
    if goal_update.target_amount is not None:
        goal.target_amount = goal_update.target_amount
    if goal_update.target_date is not None:
        goal.target_date = goal_update.target_date

    db.commit()
    db.refresh(goal)
    return goal


# Delete goal
@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: int, db: Session = Depends(get_db)):
    """
    Delete a goal by ID
    """
    goal = db.query(GoalsDB).filter(GoalsDB.id == goal_id).first()
    if not goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with id {goal_id} not found"
        )

    db.delete(goal)
    db.commit()
    return None
