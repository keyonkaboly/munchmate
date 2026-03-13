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
    restaurant = Restaurant(id=1, name="Test Restaurant")
    db.add(restaurant)

    menu_item = MenuItem(name="Pizza", restaurant_id=1, price=10)
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
    assert json_data["restaurant_id"] == 1


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
    
def test_menu_item_price_negative():

    # Insert a menu item with invalid price
    db = TestingSessionLocal() # opens a new db session connected to the SQLite test db
    bad_item = MenuItem(name="BadPizza", restaurant_id=1, price=-10) # crears a menu item object in memory, not go in db yet
    db.add(bad_item) # prepare to insert this object into the db, but not saved yet
    db.commit() # writes into new row in test db
    db.close() # release resources, prevents connection leaks 

    response = client.get("/restaurants/1/menu-items/BadPizza") # simulates real HTTP request using FastAPI's testclient 

    assert response.status_code == 400 # checks API returned
    assert response.json()["detail"] == "Price must be a positive integer"

def test_menu_item_price_zero():

    db = TestingSessionLocal()
    bad_item = MenuItem(name="FreePizza", restaurant_id=1, price=0)
    db.add(bad_item)
    db.commit()
    db.close()

    response = client.get("/restaurants/1/menu-items/FreePizza")

    assert response.status_code == 400

def test_menu_item_price_valid():

    db = TestingSessionLocal()
    good_item = MenuItem(name="Burger", restaurant_id=1, price=15)
    db.add(good_item)
    db.commit()
    db.close()

    response = client.get("/restaurants/1/menu-items/Burger")

    assert response.status_code == 200

    json_data = response.json()
    assert json_data["food_item"] == "Burger"
    assert json_data["restaurant_id"] == 1

"""Test to ensure partial menu item searching actually produces a result.
Sends a partial food string query to the searching endpoint and confirms the response contains a list including expected menu item."""
def test_search_menu_items_by_text():

    response = client.get("/restaurants/1/menu-items/search", params={"query": "Piz"})

    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)
    assert any(item["name"] == "Pizza" for item in json_data)

"""Ensures the search can handle menu items with special characters. Created query with special character and ensures it can be found using search."""
def test_search_menu_items_special_characters():

    db = TestingSessionLocal()
    item = MenuItem(name="Mac & Cheese", restaurant_id=1, price=14)
    db.add(item)
    db.commit()
    db.close()

    response = client.get("/restaurants/1/menu-items/search", params={"query": "Mac & Cheese"})

    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, list)
    assert any(menu_item["name"] == "Mac & Cheese" for menu_item in json_data)

"""Ensure that searching with a non existing restaurant id returns 404."""
def test_search_menu_items_invalid_restaurant_id():

    response = client.get("/restaurants/999/menu-items/search", params={"query": "Pizza"})

    assert response.status_code == 404

"""Ensure that menu item not at this resturant message appears when users search item thats not at the restaurant"""
def test_search_menu_items_not_found():

    response = client.get("/restaurants/1/menu-items/search", params={"query": "NotOnMenu"})

    assert response.status_code == 200
    assert response.json()["message"] == "Sorry! This restaurant does not have this menu item."

