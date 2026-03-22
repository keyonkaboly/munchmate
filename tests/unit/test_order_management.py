import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem, Order

TEST_DATABASE_URL = "sqlite:///./test_management.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup():
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


@pytest.fixture
def order_id():
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"]
    })
    return res.json()["combined_order_id"]


def test_add_item(order_id):
    res = client.post(f"/orders/{order_id}/add-item", params={"food_item": "Burger"})
    assert res.status_code == 200


def test_remove_item(order_id):
    res = client.delete(f"/orders/{order_id}/remove-item", params={"food_item": "Pizza"})
    assert res.status_code == 200


def test_update_quantity(order_id):
    res = client.patch(
        f"/orders/{order_id}/update-item",
        params={"food_item": "Pizza", "quantity": 3}
    )
    assert res.status_code == 200

    db = SessionLocal()
    items = db.query(Order).filter(
        Order.combined_order_id == order_id,
        Order.food_item == "Pizza"
    ).all()
    db.close()

    assert len(items) == 3


def test_submit(order_id):
    res = client.post(f"/orders/{order_id}/submit")
    assert res.status_code == 200

    db = SessionLocal()
    items = db.query(Order).filter(Order.combined_order_id == order_id).all()
    db.close()

    assert all(i.status == "submitted" for i in items)