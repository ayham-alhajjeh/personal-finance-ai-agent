import uuid
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Cookie, Response, BackgroundTasks, status
from sqlalchemy.orm import Session
from utils.security import hash_password, verify_password

from db.database import get_db
from models.user import UserDB
from schemas.user import UserBase, UserCreate, UserOut, UserLogin


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_session_id(session_id: Optional[str] = Cookie(None)):
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id


# Create a new user
@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with email and optional name
    """
    # Check if user with email already exists
    existing_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    hashed_password = hash_password(user.password)
    
    # Create new user
    db_user = UserDB(
        email=user.email,
        name=user.name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


# Get user by ID
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user


# Get all users
@router.get("/", response_model=List[UserOut])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users with pagination
    """
    users = db.query(UserDB).offset(skip).limit(limit).all()
    return users


# Get user by email
@router.get("/email/{email}", response_model=UserOut)
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """
    Get a user by email address
    """
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    return user


# Update user
@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserBase, db: Session = Depends(get_db)):
    """
    Update user information
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # Update fields
    if user_update.email:
        # Check if new email is already taken by another user
        existing_user = db.query(UserDB).filter(
            UserDB.email == user_update.email,
            UserDB.id != user_id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        user.email = user_update.email
    
    if user_update.name is not None:
        user.name = user_update.name
    
    db.commit()
    db.refresh(user)
    return user


# Delete user
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID
    """
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    db.delete(user)
    db.commit()
    return None

@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login user with email and password
    """
    user = db.query(UserDB).filter(UserDB.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # In real app, return a JWT token here
    return {"message": "Login successful", "user_id": user.id}