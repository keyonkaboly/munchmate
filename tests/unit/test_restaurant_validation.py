import pytest
from app.infrastructure.database.models import Restaurant, MenuItem
from conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def seed_data():
    
    db = TestingSessionLocal()
    db.query(MenuItem).delete()
    db.query(Restaurant).delete()
    db.commit()

    restaurant = Restaurant(id=1, location="123 Test St")
    db.add(restaurant)
    menu_item = MenuItem(id=1, food_item="Pizza", restaurant_id=1)
    db.add(menu_item)
    db.commit()
    db.close()
    yield

    
    db = TestingSessionLocal()
    db.query(MenuItem).delete()
    db.query(Restaurant).delete()
    db.commit()
    db.close()


def test_valid_restaurant_id(client):
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_invalid_restaurant_id(client):
    response = client.get("/restaurants/999")
    assert response.status_code == 404


def test_valid_menu_item_for_restaurant(client):
    response = client.get("/restaurants/1/menu-items/Pizza")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["food_item"] == "Pizza"
    assert json_data["restaurant_id"] == 1


def test_invalid_menu_item_for_restaurant(client):
    response = client.get("/restaurants/1/menu-items/Sushi")
    assert response.status_code == 404