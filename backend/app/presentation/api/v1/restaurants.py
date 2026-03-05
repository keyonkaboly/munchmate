"""Module for restaurant and menu item validation routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.infrastructure.database.models import Restaurant, MenuItem

# Create router for restaurant endpoints
router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.get("/{restaurant_id}")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """Check if a restaurant exists by ID."""
    # Simple lookup to see if restaurant exists
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant ID not found")

    return {"restaurant_id": restaurant.id}


@router.get("/{restaurant_id}/menu-items/{food_item}")
def get_menu_item(restaurant_id: int, food_item: str, db: Session = Depends(get_db)):
    """Validate that a food item exists and belongs to the given restaurant."""

    # First verify the restaurant exists
    rest = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if rest is None:
        raise HTTPException(status_code=404, detail="Restaurant ID not found")

    # Then check if the menu item is available at this restaurant
    item = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.name == food_item  # Match by exact name
    ).first()

    if not item:
        # Food item doesn't exist at this location
        raise HTTPException(
            status_code=404,
            detail="This food item does not exist at this restaurant"
        )

    # Build response with both pieces of info
    response = {
        "food_item": item.name,
        "restaurant_id": rest.id
    }

    return response
