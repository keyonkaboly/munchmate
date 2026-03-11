"""Module for restaurant and menu item validation routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Restaurant, MenuItem
from app.presentation.schemas.restaurant_schemas import RestaurantUpdate, RestaurantResponse

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

# updates to restaurant details, only for restaurant owners 
@router.put("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(restaurant_id: int, data: RestaurantUpdate, db: Session = Depends(get_db)): # takes rest. ID from URL and new data from the request body 
    """Allow a restaurant owner to update their restaurant's details."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first() # looks up restauraunt to see if exists
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant ID not found")

   # overwrites old values with new ones from the request `
    restaurant.name = data.name
    restaurant.description = data.description
    restaurant.hours_of_operation = data.hours_of_operation

    db.commit()
    db.refresh(restaurant)
    return restaurant