from app.data.dataset_loader import load_dataset
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.database.models import Restaurant, MenuItem


def seed_restaurants(result, db_session):
    """Seed unique restaurants from the dataset into the database."""
    uniqueRestaurants = result[['restaurant_id', 'location']].drop_duplicates(subset=['restaurant_id'])
    restaurant_count = 0

    for index, row in uniqueRestaurants.iterrows():
        restaurant_id = int(row['restaurant_id'])
        exist = db_session.query(Restaurant).filter(Restaurant.id == restaurant_id).first()

        if not exist:
            restaurant = Restaurant(id=restaurant_id, name=f"Restaurant {restaurant_id}", location=str(row['location']) if row['location'] is not None else None,)
            db_session.add(restaurant)
            restaurant_count += 1

    db_session.commit()
    return restaurant_count


def seed_menu_items(result, db_session):
    """Seed unique menu items per restaurant from the dataset."""
    uniqueMenuItems = result[['restaurant_id', 'food_item']].drop_duplicates(subset=['restaurant_id', 'food_item'])
    menu_item_count = 0

    for index, row in uniqueMenuItems.iterrows():
        restaurant_id = int(row['restaurant_id'])
        food_item = str(row['food_item'])

        exist = db_session.query(MenuItem).filter(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.name == food_item
        ).first()

        if not exist:
            menu_item = MenuItem(restaurant_id=restaurant_id, name=food_item)
            db_session.add(menu_item)
            menu_item_count += 1

    db_session.commit()
    return menu_item_count


def seed_dataset_data():
    """Load the dataset and seed restaurants plus menu items."""
    db_session = SessionLocal()

    try:
        result = load_dataset()
        restaurant_count = seed_restaurants(result, db_session)
        menu_item_count = seed_menu_items(result, db_session)

        print("Seeding complete.", restaurant_count, "restaurants seeded. ", menu_item_count, " menu items seeded.")

        return restaurant_count, menu_item_count

    except Exception as e:
        db_session.rollback()
        print("Error when attempting to seed database:", e)
        raise

    finally:
        db_session.close()
