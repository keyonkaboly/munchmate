import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem


# Used SQLite to setup the ds
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():

    #override the db dependency to make sure that during test we don't mess with production data
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# here the dep is being overriden
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():

    #Create tables and seed test data before each test, drop after.
    #I usually prefer this approach to keep tests isolated

    Base.metadata.create_all(bind=engine)

    # add some test data
    db = TestingSessionLocal()
    restaurant = Restaurant(id=1, location="123 Test St")
    db.add(restaurant)

    menu_item = MenuItem(id=1, food_item="Pizza", restaurant_id=1)
    db.add(menu_item)

    db.commit()
    db.close()

    yield

    # here it would reset and clean up the run after the test
    Base.metadata.drop_all(bind=engine)


# I'm initializing the test client here
client = TestClient(app)


def test_valid_restaurant_id():
    #Check that a valid restaurant ID returns 200.
    #Testing the happy path here

    response = client.get("/restaurants/1")

    assert response.status_code == 200

    # Verify response body contains expected data
    json_data = response.json()
    assert json_data["id"] == 1


def test_invalid_restaurant_id():

    #Check that an invalid restaurant ID returns 404.
    #This should handle the case where restaurant doesn't exist

    response = client.get("/restaurants/999")  # Using 999 as non-existent ID

    assert response.status_code == 404


def test_valid_menu_item_for_restaurant():

    #Check that a valid food item at the correct restaurant returns 200.
    #Let's make sure the menu item retrieval works properly

    response = client.get("/restaurants/1/menu-items/Pizza")

    assert response.status_code == 200

    json_data = response.json()
    assert json_data["food_item"] == "Pizza"
    assert json_data["restaurant_id"] == 1


def test_invalid_menu_item_for_restaurant():

    #Check that a food item not at the restaurant returns 404.
    #Edge case: requesting an item that doesn't exist at this restaurant

    response = client.get("/restaurants/1/menu-items/Sushi")

    # Should return 404 since Sushi isn't on the menu for restaurant 1
    assert response.status_code == 404
