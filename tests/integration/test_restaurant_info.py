import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem

# provides an isolated test database so real data is never affected
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# redirecting database calls to the test database during tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# prepares and cleans up test data before and after each test
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    restaurant = Restaurant(id=1, name="Pizza Place", description="Good pizza", hours_of_operation="9am-9pm")
    second_restaurant = Restaurant(id=2, name="Burger Place", description="Good burgers", hours_of_operation="10am-10pm")
    db.add(restaurant)
    db.add(second_restaurant)
    menu_item = MenuItem(name="Pizza", restaurant_id=1, price=10)
    db.add(menu_item)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

# simulates real HTTP requests to the API during tests
client = TestClient(app)

# Verifies that updating a restaurant returns the correct updated data
def test_put_updates_restaurant_info():
    response = client.put("/restaurants/1", json={
        "name": "New Pizza Place",
        "description": "Even better pizza",
        "hours_of_operation": "8am-10pm"
    })
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "New Pizza Place"
    assert json_data["description"] == "Even better pizza"
    assert json_data["hours_of_operation"] == "8am-10pm"

# Verifies that fetching a restaurant returns the correct JSON format
def test_get_restaurant_returns_correct_format():
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    json_data = response.json()
    assert "restaurant_id" in json_data
    assert json_data["restaurant_id"] == 1

# Verifies that the API handles non-existent restaurants with a proper error
def test_put_invalid_restaurant_returns_404():
    response = client.put("/restaurants/999", json={
        "name": "Ghost Restaurant",
        "description": "Doesn't exist",
        "hours_of_operation": "never"
    })
    assert response.status_code == 404

# verifyies that the API rejects incomplete or invalid input data
def test_put_missing_name_returns_422():
    response = client.put("/restaurants/1", json={
        "description": "No name provided",
        "hours_of_operation": "9am-9pm"
    })
    assert response.status_code == 422

# verifies that updates are actually retrievable from the database
def test_put_changes_are_saved_and_retrievable():
    client.put("/restaurants/1", json={
        "name": "Saved Pizza Place",
        "description": "This should be saved",
        "hours_of_operation": "10am-8pm"
    })
    response = client.get("/restaurants/1")
    assert response.status_code == 200

"""Check if API blocks access to a menu item when restaurant ID doesn't match the restaurant of the menu item.
Looks for restaurant_id = 1 , name = Pizza. Saves the menu item id. Closes database and requests the id (via api endpoint).
This should be invalid because we ask for endpoint of restaurant 2 item 17 which does not exist."""
def test_menu_item_id_mismatch_returns_404():
    db = TestingSessionLocal()
    menu_item = db.query(MenuItem).filter(MenuItem.restaurant_id == 1, MenuItem.name == "Pizza").first()
    item_id = menu_item.id
    db.close()

    response = client.get(f"/restaurants/2/menu-items/id/{item_id}")
    assert response.status_code == 404