import pytest
from app.infrastructure.database.models import Restaurant, MenuItem
from conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def seed_restaurants():
 
    db = TestingSessionLocal()
    db.query(MenuItem).delete()
    db.query(Restaurant).delete()
    db.commit()

    restaurant = Restaurant(id=1, location="City_3", food_item="Pizza")
    second_restaurant = Restaurant(id=2, location="City_8", food_item="Burger")
    db.add(restaurant)
    db.add(second_restaurant)
    menu_item = MenuItem(id=1, food_item="Pizza", restaurant_id=1, price=10)
    db.add(menu_item)
    db.commit()
    db.close()
    yield

   
    db = TestingSessionLocal()
    db.query(MenuItem).delete()
    db.query(Restaurant).delete()
    db.commit()
    db.close()


def test_put_updates_restaurant_info(client):
    response = client.put("/restaurants/1", json={
        "id": 1,
        "location": "City_4",
        "food_item": "Pasta"
    })
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["location"] == "City_4"
    assert json_data["food_item"] == "Pasta"


def test_get_restaurant_returns_correct_format(client):
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    json_data = response.json()
    assert "id" in json_data
    assert json_data["id"] == 1


def test_put_invalid_restaurant_returns_404(client):
    response = client.put("/restaurants/999", json={
        "id": 999,
        "location": "Doesn't exist",
        "food_item": "never"
    })
    assert response.status_code == 404


def test_put_missing_name_returns_422(client):
    response = client.put("/restaurants/1", json={
        "location": "No id provided",
        "food_item": "Pizza"
    })
    assert response.status_code == 422


def test_put_changes_are_saved_and_retrievable(client):
    client.put("/restaurants/1", json={
        "id": 1,
        "location": "City_5",
        "food_item": "Burger"
    })
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["location"] == "City_5"
    assert json_data["food_item"] == "Burger"