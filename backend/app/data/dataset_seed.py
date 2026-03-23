from app.data.dataset_loader import load_dataset
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.database.models import Restaurant, MenuItem, Order


def seed_restaurants(result, db_session):
    """Seed unique restaurants from the dataset into the database."""
    CUISINE_MAP = {
    "Pizza": "Italian", "Pasta": "Italian",
    "Sushi": "Asian", "Briyani rice": "Asian", "Chicken rice": "Asian", "Dumplings": "Asian",
    "Burritos": "Mexican", "Taccos": "Mexican",
    "Burger": "American", "Chicken wings": "American", "Fried chicken": "American",
    "Shawarma": "Mediterranean", "Soup": "Mediterranean", "Salad": "Mediterranean",
    "Whole cake": "Desserts & Drinks", "Cookie": "Desserts & Drinks", "Cup cake": "Desserts & Drinks",
    "CoffeeBoba tea": "Desserts & Drinks", "PastrySmoothie": "Desserts & Drinks",
    "Beef pie": "Other", "Chicken pie": "Other"
}
    
    unique_restaurants = result[['restaurant_id', 'food_item', 'location']].drop_duplicates(subset=['restaurant_id'])
    restaurant_count = 0

    from app.utils.filters import apply_dietary_filters
    vegetarian_items = {"Salad", "Soup", "Whole cake", "Cookie", "Cup cake", "PastrySmoothie"}
    halal_items = {"Briyani rice", "Chicken rice", "Shawarma", "Dumplings", "Sushi"}

    for index, row in unique_restaurants.iterrows():
        restaurant_id = int(row['restaurant_id'])
        cuisine = CUISINE_MAP.get(row['food_item'], "Other")
        location = str(row['location'])
        food_item = str(row['food_item'])
        is_vegetarian = food_item in vegetarian_items
        is_halal = food_item in halal_items or is_vegetarian

        exist = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

        if not exist:
            restaurant = Restaurant(
                id=restaurant_id,
                location=location,
                food_item=food_item,
                is_halal=is_halal,
                is_vegetarian=is_vegetarian,
                cuisine_type=cuisine,
            )
            db_session.add(restaurant)
            restaurant_count += 1
    return restaurant_count


def seed_menu_items(result, db_session):
    """Seed unique menu items per restaurant from the dataset."""
    unique_menu_items = result[['restaurant_id', 'food_item', 'order_value']].drop_duplicates(subset=['restaurant_id', 'food_item'])
    menu_item_count = 0

    for index, row in unique_menu_items.iterrows():
        restaurant_id = int(row['restaurant_id'])
        food_item = str(row['food_item'])
        price = float(row['order_value'])
        is_halal = False
        is_vegetarian = False

        exist = db_session.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.food_item == food_item
        ).first()

        if not exist:
            menu_item = MenuItem(restaurant_id=restaurant_id, food_item=food_item, price=price, is_halal=is_halal, is_vegetarian=is_vegetarian)
            db_session.add(menu_item)
            menu_item_count += 1
    return menu_item_count

"""Seed unique menu items per restaurant from the dataset. For orders we calculate total cost (rnd to 2 decimal)."""
def seed_order_data(result, db_session):
    uniqueOrders = result[['order_id', 'customer_id', 'restaurant_id', 'order_value']].drop_duplicates(subset=['order_id'])
    order_count = 0

    for index, row in uniqueOrders.iterrows():
        order_id = str(row['order_id'])
        try:
            customer_id = int(row['customer_id'])
        except (ValueError, TypeError):
            continue
        restaurant_id = int(row['restaurant_id'])
        subtotal = float(row['order_value'])
        tax = round((subtotal) * (0.12), 2)
        delivery_cost = 5.00
        total_cost = round(subtotal + tax + delivery_cost, 2)

        exist = db_session.query(Order).filter(Order.order_id == order_id).first()

        if not exist:
            order = Order(order_id=order_id, customer_id=customer_id, restaurant_id=restaurant_id, subtotal=subtotal, tax=tax,delivery_cost=delivery_cost, total_cost=total_cost)
            db_session.add(order)
            order_count += 1
    db_session.commit()
    return order_count


def seed_dataset_data():
    """Load the dataset and seed restaurants plus menu items."""
    db_session = SessionLocal()

    try:
        result = load_dataset()
        restaurant_count = seed_restaurants(result, db_session)
        menu_item_count = seed_menu_items(result, db_session)
        order_count = seed_order_data(result, db_session)
        return restaurant_count, menu_item_count, order_count
    except Exception as e:
        db_session.rollback()
        raise

    finally:
        db_session.close()
        
if __name__ == "__main__":
    seed_dataset_data()