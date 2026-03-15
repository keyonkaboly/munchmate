import pytest
from app.infrastructure.database.models import Restaurant, MenuItem
from conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def seed_restaurants():
    
    db = TestingSessionLocal()
    db.query(MenuItem).delete()
    db.query(Restaurant).delete()
    db.commit()

    db.add(Restaurant(id=1, location="City_1", is_halal=True, is_vegetarian=False, cuisine_type="American"))
    db.add(Restaurant(id=2, location="City_10", is_halal=False, is_vegetarian=True, cuisine_type="Italian"))
    db.add(Restaurant(id=3, location="City_2", is_halal=False, is_vegetarian=False, cuisine_type="Asian"))
    db.commit()
    db.close()
    yield

    db = TestingSessionLocal()
    db.query(MenuItem).delete()
    db.query(Restaurant).delete()
    db.commit()
    db.close()


def test_filter_by_halal(client):
    response = client.get("/restaurants/?is_halal=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["location"] == "City_1"


def test_filter_by_vegetarian(client):
    response = client.get("/restaurants/?is_vegetarian=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["location"] == "City_10"


def test_no_filter_returns_all(client):
    response = client.get("/restaurants/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3


def test_filter_no_results(client):
    response = client.get("/restaurants/?is_halal=true&is_vegetarian=true")
    assert response.status_code == 200
    assert response.json() == {"message": "No restaurants found"}


def test_filter_by_cuisine_type(client):
    response = client.get("/restaurants/?cuisine_type=Italian")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["cuisine_type"] == "Italian"


def test_pagination_first_page(client):
    db = TestingSessionLocal()
    for i in range(4, 26):
        db.add(Restaurant(id=i, location=f"Restaurant {i}", is_halal=False, is_vegetarian=False))
    db.commit()
    db.close()

    data = client.get("/restaurants/?page=1&page_size=20").json()
    assert len(data["items"]) == 20
    assert data["total"] == 25
    assert data["page"] == 1
    assert data["total_pages"] == 2


def test_pagination_second_page(client):
    db = TestingSessionLocal()
    for i in range(4, 26):
        db.add(Restaurant(id=i, location=f"Restaurant {i}", is_halal=False, is_vegetarian=False))
    db.commit()
    db.close()

    data = client.get("/restaurants/?page=2&page_size=20").json()
    assert len(data["items"]) == 5
    assert data["page"] == 2