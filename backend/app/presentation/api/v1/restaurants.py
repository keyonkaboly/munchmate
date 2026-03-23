"""Module for restaurant and menu item validation routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Restaurant, MenuItem, Order, Customer
from app.presentation.schemas.restaurant_schemas import RestaurantUpdate, RestaurantResponse, MenuItemNameUpdate
from app.utils.filters import apply_dietary_filters
from app.utils.pagination import paginate
from app.application.services.authentication_service import get_current_user

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

    result = paginate(query, page=page, page_size=page_size)
    result["items"] = [RestaurantResponse.model_validate(item).model_dump() for item in result["items"]]
    return result

@router.get("/{restaurant_id}")
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant ID not found")

    menu_items = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id).all()

    menu_items_list = []
    for item in menu_items:
        menu_items_list.append( {"food_item": item.food_item, "price": item.price, "is_halal": item.is_halal,"is_vegetarian": item.is_vegetarian})
    
    response = restaurant.__dict__.copy()
    response["menu_items"] = menu_items_list
    return response

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
@router.get("/orders/{order_id}", response_model=RestaurantResponse)
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


@router.put("/{restaurant_id}/menu-items/{food_item}")
def rename_menu_item(restaurant_id: int, food_item: str, data: MenuItemNameUpdate, manager_user_id: int = Query(...), db: Session = Depends(get_db)):
    manager = db.query(Customer).filter(Customer.id == manager_user_id).first()
    if not manager or manager.user_type != "restaurant_manager":
        raise HTTPException(status_code=403, detail="Only restaurant managers can perform this action")

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant ID not found")

    menu_item = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id, MenuItem.food_item == food_item).first()

    if not menu_item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    exists = db.query(MenuItem).filter(MenuItem.restaurant_id == restaurant_id, MenuItem.food_item == data.food_item).first()

    if exists and data.food_item != food_item:
        raise HTTPException(status_code=409, detail="Menu item name already exists with this restaurant id ")

    menu_item.food_item = data.food_item
    db.commit()
    db.refresh(menu_item)

    return {"restaurant_id": restaurant_id, "food_item": menu_item.food_item}


#helper func
def require_restaurant_manager(current_user: Customer = Depends(get_current_user)):
    if current_user.user_type != "restaurant_manager":
        raise HTTPException(
            status_code=403,
            detail="Only restaurant managers can access this feature"
        )
    return current_user

#this func so only restaurant manager can access
@router.get("/{restaurant_id}/orders")
def get_restaurant_orders(
    restaurant_id: int,
    current_user: Customer = Depends(require_restaurant_manager),
    db: Session = Depends(get_db)
):
    if current_user.restaurant_manager_restaurant_id != restaurant_id:
        raise HTTPException(
            status_code=403,
            detail="You can only access orders for your own restaurant"
        )

    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant ID not found")

    orders = db.query(Order).filter(Order.restaurant_id == restaurant_id).all()

    return {
        "restaurant_id": restaurant_id,
        "orders": orders
    }