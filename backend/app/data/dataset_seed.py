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
    
    uniqueRestaurants = result[['restaurant_id', 'food_item', 'location']].drop_duplicates(subset=['restaurant_id'])
    restaurant_count = 0

    for index, row in uniqueRestaurants.iterrows():
        restaurant_id = int(row['restaurant_id'])
        cuisine = CUISINE_MAP.get(row['food_item'], "Other")
        location = str(row['location'])
        food_item = str(row['food_item'])
        is_halal = False
        is_vegetarian = False

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
    uniqueMenuItems = result[['restaurant_id', 'food_item', 'order_value']].drop_duplicates(subset=['restaurant_id', 'food_item'])
    menu_item_count = 0

    for index, row in uniqueMenuItems.iterrows():
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
    uniqueOrders = result[['order_id', 'customer_id', 'restaurant_id', 'order_value', 'food_item', 'delivery_method', 'delivery_distance', 'delivery_delay',
                            'route_taken', 'route_type', 'route_efficiency' ]].drop_duplicates(subset=['order_id'])
    order_count = 0

    for index, row in uniqueOrders.iterrows():
        order_id = str(row['order_id'])
        customer_id = str(row['customer_id'])
        restaurant_id = int(row['restaurant_id'])
        subtotal = float(row['order_value'])
        tax = round((subtotal) * (0.12), 2)
        delivery_cost = 5.00
        total_cost = round(subtotal + tax + delivery_cost, 2)
    
        delivery_method = str(row['delivery_method'])
        delivery_distance = float(row['delivery_distance'])
        delivery_delay = float(row['delivery_delay'])
        route_taken = str(row['route_taken'])
        route_type = str(row['route_type'])
        route_efficiency = float(row['route_efficiency'])

        exist = db_session.query(Order).filter(Order.order_id == order_id).first()

        if not exist:
            order = Order(order_id=order_id, customer_id=customer_id, restaurant_id=restaurant_id, subtotal=subtotal, tax=tax,delivery_cost=delivery_cost, total_cost=total_cost, food_item=food_item, delivery_cost=delivery_cost, delivery_method=delivery_method, delivery_distance=delivery_distance, delivery_delay=delivery_delay, route_taken=route_taken, route_type=route_type, route_efficiency=route_efficiency, status="seeded")
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

        print("Seeding complete. ", restaurant_count, "restaurants seeded. ", menu_item_count, " menu items seeded ", order_count, " orders seeded.")

        return restaurant_count, menu_item_count, order_count

    except Exception as e:
        db_session.rollback()
        print("Error when attempting to seed database:", e)
        raise

    finally:
        db_session.close()

def seed_customers(result, db_session):
    from app.infrastructure.database.models import Customer
    
    uniqueCustomers = result[['customer_id']].drop_duplicates(subset=['customer_id'])
    customer_count = 0

    for index, row in uniqueCustomers.iterrows():
        customer_id = str(row['customer_id'])
        exist = db_session.query(Customer).filter(Customer.id == customer_id).first()
        if not exist:
            customer = Customer(id=customer_id)
            db_session.add(customer)
            customer_count += 1

    db_session.commit()
    return customer_count