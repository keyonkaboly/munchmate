from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.db.database import get_db
from app.infrastructure.database.models import Restaurant, MenuItem

# Setting up the router with prefix and tags
router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# This endpoint checks if a restaurant exists by ID
# TODO: Maybe add more restaurant details later?
@router.get("/{restaurant_id}")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    # Query the database for the restaurant
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    # If restaurant doesn't exist, return 404
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant ID not found")
    


    
    # Return the restaurant ID (keeping it simple for now)
    return {"restaurant_id": restaurant.id}
# This one validates both restaurant and menu item
# Note: food_item is passed as a string in the URL
@router.get("/{restaurant_id}/menu-items/{food_item}")
def get_menu_item(restaurant_id: int, food_item: str, db: Session = Depends(get_db)):
    # First, let's check if the restaurant even exists
    rest = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if rest is None:  # Using 'is None' instead of 'not' here
        raise HTTPException(status_code=404, detail="Restaurant ID not found")

    # Now check if the menu item exists for this restaurant
    # Filtering by both restaurant_id and item name
    item = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.name == food_item
    ).first()
    
    # If the item doesn't exist at this restaurant, throw error
    if not item:
        raise HTTPException(
            status_code=404, 
            detail="This food item does not exist at this restaurant"
        )

    # All good! Return the details
    response = {
        "food_item": item.name,
        "restaurant_id": rest.id  # Using 'rest' from earlier query
    }
    
    return response