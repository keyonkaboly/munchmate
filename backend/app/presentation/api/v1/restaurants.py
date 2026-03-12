"""Module for restaurant and menu item validation routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Restaurant, MenuItem
from app.presentation.schemas.restaurant_schemas import MenuItemUpdate, RestaurantUpdate, RestaurantResponse
from app.utils.filters import apply_dietary_filters

# Create router for restaurant endpoints
router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("/")
def get_filtered_restaurants(
    is_halal: bool = None,
    is_vegetarian: bool = None,
    db: Session = Depends(get_db)
):
    "Return restaurants filtered by dietary options."
    restaurants = apply_dietary_filters(db, is_halal=is_halal, is_vegetarian=is_vegetarian)

    if not restaurants:
        return {"message": "No restaurants found"}

    return restaurants

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

    # checks if price is a positive integer 
    if item.price is None or item.price <= 0:
        raise HTTPException(
            status_code=400,
            detail="Price must be a positive integer"
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

   # overwrites old values with new ones from the request
    restaurant.name = data.name
    restaurant.description = data.description
    restaurant.hours_of_operation = data.hours_of_operation

    db.commit()
    db.refresh(restaurant)
    return restaurant

@router.get("/{restaurant_id}/menu-items")
def get_menu_items(restaurant_id: int, db: Session = Depends(get_db)):
    """Return all menu items that belong to a specific restaurant.
    Validate restaurant existence, search menu item rows filtered by restaurant_id. Then return list
    404 if restaurant_id dne."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found. ")
    menu_items = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()
    return menu_items


@router.get("/{restaurant_id}/menu-items/{menu_item_id}")
def get_menu_item_by_id(restaurant_id: int, menu_item_id: int, db: Session = Depends(get_db)):
    """Return one menu item only if it belongs to the given restaurant.
    Validate restaurant existence. Search for menu item using id's for menu item and restaurant.
    Return item. Raises 404 if dne."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found. ")

    menu_item = db.query(MenuItem).filter(
        MenuItem.id == menu_item_id,
        MenuItem.restaurant_id == restaurant_id
    ).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found. ")
    return menu_item


@router.patch("/{restaurant_id}/menu-items/{menu_item_id}")
def update_menu_item(restaurant_id: int, menu_item_id: int, data: MenuItemUpdate, db: Session = Depends(get_db)):
    """Update allowed menu-item fields for a specific restaurant item.
    Validate restaurant existence, validate menu item exists for that restaurant.
    Reads only submitted fields "excluse_unset=True". Applies updates for fields present on model, then commit/refresh
    MenuItemUpdate schema controls what fields are accepted.
    Raises 404 if menuItem/restaurant not found."""
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found. ")

    menu_item = db.query(MenuItem).filter(
        MenuItem.id == menu_item_id,
        MenuItem.restaurant_id == restaurant_id
    ).first()
    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found. ")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(menu_item, field):
            setattr(menu_item, field, value)

    db.commit()
    db.refresh(menu_item)
    return menu_item