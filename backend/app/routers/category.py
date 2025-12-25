from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.categories import CategoriesDB
from models.user import UserDB
from schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from utils.auth import get_current_user

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


# Create a new category
@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new category for the authenticated user
    """
    # Check if category with same name already exists for this user
    existing_category = db.query(CategoriesDB).filter(
        CategoriesDB.user_id == current_user.id,
        CategoriesDB.name == category.name
    ).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category.name}' already exists"
        )

    # Create category
    db_category = CategoriesDB(
        user_id=current_user.id,
        name=category.name,
        type=category.type
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


# Get all categories for current user
@router.get("/", response_model=List[CategoryOut])
def get_my_categories(
    skip: int = 0,
    limit: int = 100,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all categories for the authenticated user with pagination
    """
    categories = db.query(CategoriesDB).filter(
        CategoriesDB.user_id == current_user.id
    ).offset(skip).limit(limit).all()

    return categories


# Get category by ID
@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific category by ID (must belong to user)
    """
    category = db.query(CategoriesDB).filter(
        CategoriesDB.id == category_id,
        CategoriesDB.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found or doesn't belong to you"
        )
    return category


# Get categories by type
@router.get("/type/{category_type}", response_model=List[CategoryOut])
def get_categories_by_type(
    category_type: str,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all categories of a specific type for authenticated user
    """
    categories = db.query(CategoriesDB).filter(
        CategoriesDB.user_id == current_user.id,
        CategoriesDB.type == category_type
    ).all()

    return categories


# Update category
@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a category (must belong to user)
    """
    category = db.query(CategoriesDB).filter(
        CategoriesDB.id == category_id,
        CategoriesDB.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found or doesn't belong to you"
        )

    # Update fields if provided
    if category_update.name is not None:
        # Check if new name already exists for this user
        existing_category = db.query(CategoriesDB).filter(
            CategoriesDB.user_id == current_user.id,
            CategoriesDB.name == category_update.name,
            CategoriesDB.id != category_id
        ).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_update.name}' already exists"
            )
        category.name = category_update.name

    if category_update.type is not None:
        category.type = category_update.type

    db.commit()
    db.refresh(category)
    return category


# Delete category
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a category by ID (must belong to user)
    """
    category = db.query(CategoriesDB).filter(
        CategoriesDB.id == category_id,
        CategoriesDB.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found or doesn't belong to you"
        )

    db.delete(category)
    db.commit()
    return None
