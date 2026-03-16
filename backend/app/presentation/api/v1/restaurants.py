"""Module for restaurant and menu item validation routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Restaurant, MenuItem, Order
from app.presentation.schemas.restaurant_schemas import RestaurantUpdate, RestaurantResponse
from app.utils.filters import apply_dietary_filters
from app.utils.pagination import paginate

# Create router for restaurant endpoints
router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("/")
def get_filtered_restaurants(
    is_halal: bool = None,
    is_vegetarian: bool = None,
    cuisine_type: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=20),
    db: Session = Depends(get_db) 
):
    "Returns restaurants filtered by dietary options and includes page numbers."
    query = apply_dietary_filters(db, is_halal=is_halal, is_vegetarian=is_vegetarian, cuisine_type=cuisine_type, return_query=True)

    if query.count() == 0:
        return {"message": "No restaurants found"}

    return paginate(query, page=page, page_size=page_size)

@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant ID not found")
    
    return restaurant

"""Search for menu items within a specific restaurant using string text query.
The return is any matches that partially match the string query text.
If restaurant id doesn't exist 404 occurs. If nothing matches an empty list is returned."""
@router.get("/{restaurant_id}/menu-items/search")
def search_menu_items(
    restaurant_id: int,
    query: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=20),
    db: Session = Depends(get_db)
):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found. ")

    search_query = db.query(MenuItem).filter(
        MenuItem.restaurant_id == restaurant_id,
        MenuItem.food_item.ilike(f"%{query}%")
    )
    return paginate(search_query, page=page, page_size=page_size)

"""Getting order by using order_id"""
@router.get("/{order_id}", response_model=RestaurantResponse)
def get_order(order_id: str, db: Session = Depends(get_db)):
    exist = db.query(Order).filter(Order.order_id == order_id).first()

    if exist is None:
        raise HTTPException(status_code=404, detail="Order not found.")
       
    return exist

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
        MenuItem.food_item == food_item  # Match by exact name
    ).first()

    if not item:
        # Food item doesn't exist at this location
        raise HTTPException(
            status_code=404,
            detail="This food item does not exist at this restaurant"
        )

    # Build response with both pieces of info
    response = {
        "food_item": item.food_item,
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
    restaurant.id = data.id
    restaurant.location = data.location
    restaurant.food_item = data.food_item

    db.commit()
    db.refresh(restaurant)
    return restaurant
