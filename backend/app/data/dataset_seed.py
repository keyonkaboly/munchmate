from app.data.dataset_loader import load_dataset
from app.infrastructure.database.database import SessionLocal
from app.infrastructure.database.models import Restaurant


# Inserts restaurants into the database. Loads in the CSV Dataset from dataset_loader.
# Creates restaurant if doesn't exist yet.
def restaurants_and_menuItems():
    db_session = SessionLocal()

    try:
        # Within the try, attempt to grab from dataset_loader
        result = load_dataset()

        # Keeps one row for each restaurant
        uniqueRestaurants = result[['restaurant_id', 'location']].drop_duplicates(subset=['restaurant_id'])

        # Count to track number of restaurants grabbed from csv
        count = 0

        for index, row in uniqueRestaurants.iterrows():
            # Skip if restaurant already exists in .csv
            exist = db_session.query(Restaurant).filter(Restaurant.id == int(row['restaurant_id'])).first()

        if not exist:
            restaurant = Restaurant(id = int(row['restaurant.id']), name = f"Restaurant {int(row['restaurant_id'])}", address = str(row['location']))

                db_session.add(restaurant)
                count += 1

        db_session.commit()

        print("Seeding complete.", count, "restaurants seeded.")

        return count

    except Exception as e:
        db_session.rollback()
        
        print("Error seeding database:", e)
        raise

    finally:
        db_session.close()
