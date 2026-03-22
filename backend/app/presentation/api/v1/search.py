"""Module for global search bar endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Restaurant


router = APIRouter(prefix="/search", tags=["search"])


@router.get("/restaurants")
def search_restaurants(restaurant_id: int, db: Session = Depends(get_db)):
    """Search for a restaurant by its ID."""
    if restaurant_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Restaurant ID must be a positive integer"
        )

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    if not restaurant:
        return {"results": [], "message": "No restaurant found with that ID"}

    return {
        "results": [
            {
                "restaurant_id": restaurant.id,
                "location": restaurant.location,
                "food_item": restaurant.food_item,
                "cuisine_type": restaurant.cuisine_type,
                "is_halal": restaurant.is_halal,
                "is_vegetarian": restaurant.is_vegetarian
            }
        ]
    }