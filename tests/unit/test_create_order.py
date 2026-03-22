import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem

TEST_DATABASE_URL = "sqlite:///./test_create.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup():
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    db.add(Restaurant(id=1))
    db.add(MenuItem(id=1, restaurant_id=1, food_item="Pizza", price=10))
    db.add(MenuItem(id=2, restaurant_id=1, food_item="Burger", price=8))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = previous_overrides


def test_create_order_success():
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza", "Burger"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "combined_order_id" in data
    assert data["count"] == 2


def test_create_order_empty():
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": []
    })
    assert res.status_code == 400


def test_create_invalid_item():
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Sushi"]
    })
    assert res.status_code == 404


def test_complete_order_populates_delivery_info():
    db = SessionLocal()

    # create the order via API
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza", "Burger"]
    })
    assert res.status_code == 200
    order_id = res.json()["combined_order_id"]

    # seed some Order rows with delivery data so get_most_restrictive_delivery has something to query
    from app.infrastructure.database.models import Order
    db.add(Order(
        order_id="seed-1",
        restaurant_id=1,
        food_item="Pizza",
        status="Created",
        delivery_method="Bike",
        delivery_distance=5.0,
        delivery_delay=10.0,
        route_taken="Route A",
        route_type="Mixed",
        route_efficiency=0.8,
        subtotal=10.0, tax=1.2, delivery_cost=5.0, total_cost=16.2
    ))
    db.add(Order(
        order_id="seed-2",
        restaurant_id=1,
        food_item="Burger",
        status="Created",
        delivery_method="Car",
        delivery_distance=8.0,
        delivery_delay=20.0,
        route_taken="Route B",
        route_type="Car-only",
        route_efficiency=0.5,
        subtotal=8.0, tax=0.96, delivery_cost=5.0, total_cost=13.96
    ))
    db.commit()
    db.close()

    # move order through the status flow
    client.post(f"/orders/{order_id}/submit")
    client.patch(f"/orders/{order_id}/in-progress")
    res = client.patch(f"/orders/{order_id}/complete")

    assert res.status_code == 200
    delivery_info = res.json()["delivery_info"]

    # Car is most restrictive, 20.0 is max delay, 8.0 is max distance etc
    assert delivery_info["delivery_method"] == "Car"
    assert delivery_info["delivery_delay"] == 20.0
    assert delivery_info["delivery_distance"] == 8.0
    assert delivery_info["route_type"] == "Car-only"
    assert delivery_info["route_efficiency"] == 0.5
    assert delivery_info["route_taken"] == "Route B"