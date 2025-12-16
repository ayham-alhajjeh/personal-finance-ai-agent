from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.categories import CategoriesDB
from schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(
    prefix="/categories",
    tags=["categories"]
)


# Create a new category
@router.post("/", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Create a new category for a user
    """
    # Verify user exists
    from models.user import UserDB
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )

    # Check if category with same name already exists for this user
    existing_category = db.query(CategoriesDB).filter(
        CategoriesDB.user_id == user_id,
        CategoriesDB.name == category.name
    ).first()
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category.name}' already exists for this user"
        )

    # Create category
    db_category = CategoriesDB(
        user_id=user_id,
        name=category.name,
        type=category.type
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


# Get category by ID
@router.get("/{category_id}", response_model=CategoryOut)
def get_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a specific category by ID
    """
    category = db.query(CategoriesDB).filter(CategoriesDB.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    return category


# Get all categories for a user
@router.get("/user/{user_id}", response_model=List[CategoryOut])
def get_user_categories(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all categories for a specific user with pagination
    """
    categories = db.query(CategoriesDB).filter(
        CategoriesDB.user_id == user_id
    ).offset(skip).limit(limit).all()

    return categories


# Get categories by type
@router.get("/user/{user_id}/type/{category_type}", response_model=List[CategoryOut])
def get_categories_by_type(
    user_id: int,
    category_type: str,
    db: Session = Depends(get_db)
):
    """
    Get all categories of a specific type for a user
    """
    categories = db.query(CategoriesDB).filter(
        CategoriesDB.user_id == user_id,
        CategoriesDB.type == category_type
    ).all()

    return categories


# Update category
@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a category
    """
    category = db.query(CategoriesDB).filter(CategoriesDB.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )

    # Update fields if provided
    if category_update.name is not None:
        # Check if new name already exists for this user
        existing_category = db.query(CategoriesDB).filter(
            CategoriesDB.user_id == category.user_id,
            CategoriesDB.name == category_update.name,
            CategoriesDB.id != category_id
        ).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category_update.name}' already exists for this user"
            )
        category.name = category_update.name

    if category_update.type is not None:
        category.type = category_update.type

    db.commit()
    db.refresh(category)
    return category


# Delete category
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """
    Delete a category by ID
    """
    category = db.query(CategoriesDB).filter(CategoriesDB.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )

    db.delete(category)
    db.commit()
    return None
