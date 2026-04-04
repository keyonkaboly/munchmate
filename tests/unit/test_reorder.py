import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem, Customer

TEST_DATABASE_URL = "sqlite:///./test_reorder.db"
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

def create_and_complete_order(customer_id: int = 1):
    res = client.post("/orders/create", json={
        "customer_id": customer_id,
        "restaurant_id": 1,
        "food_items": ["Pizza", "Burger"]
    })
    assert res.status_code == 200
    order_id = res.json()["order_id"]

    client.post(f"/orders/{order_id}/submit")
    client.patch(f"/orders/{order_id}/complete")

    return order_id

def test_reorder_success():
    order_id = create_and_complete_order(customer_id=1)
    res = client.post(f"/orders/{order_id}/reorder?customer_id=1")
    assert res.status_code == 200
    data = res.json()
    assert "new_order_id" in data
    assert data["new_order_id"] != order_id
    assert data["count"] == 2
    assert set(data["food_items"]) == {"Pizza", "Burger"}

def test_reorder_creates_independent_order():
    order_id = create_and_complete_order(customer_id=1)
    res = client.post(f"/orders/{order_id}/reorder?customer_id=1")
    assert res.status_code == 200
    new_order_id = res.json()["new_order_id"]

    cancel_res = client.patch(f"/orders/{new_order_id}/cancel")
    assert cancel_res.status_code == 200

    original = client.get(f"/orders/{order_id}")
    assert original.status_code == 200

def test_reorder_wrong_customer():
    order_id = create_and_complete_order(customer_id=1)
    res = client.post(f"/orders/{order_id}/reorder?customer_id=99")
    assert res.status_code == 403

def test_reorder_invalid_order_id():
    res = client.post("/orders/nonexistent-id/reorder?customer_id=1")
    assert res.status_code == 404