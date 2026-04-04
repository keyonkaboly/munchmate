import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem

TEST_DATABASE_URL = "sqlite:///./test_early_refund.db"
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
    db.add(Restaurant(id=1, location="1 Test St"))
    db.add(MenuItem(id=1, restaurant_id=1, food_item="Pizza", price=10.0))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides = previous_overrides


def _create_paid_order():
    order_response = client.post(
        "/orders/create",
        json={"customer_id": 1, "restaurant_id": 1, "food_items": ["Pizza"]},
    )
    assert order_response.status_code == 200
    oid = order_response.json()["combined_order_id"]
    client.post(f"/checkout/orders/{oid}/place")
    pay = client.post(
        "/payments/",
        json={"order_id": oid, "total_cost": 25.99, "card_number": "4111111111111111"},
    )
    assert pay.status_code == 200
    assert pay.json()["success"] is True
    return oid


def test_cancel_with_refund_success():
    oid = _create_paid_order()
    response = client.post(f"/orders/{oid}/cancel-with-refund")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == oid
    assert data["refund_amount"] == 8.0


def test_cancel_with_refund_rejects_without_payment():
    order_response = client.post(
        "/orders/create",
        json={"customer_id": 1, "restaurant_id": 1, "food_items": ["Pizza"]},
    )
    oid = order_response.json()["combined_order_id"]
    response = client.post(f"/orders/{oid}/cancel-with-refund")
    assert response.status_code == 400
    assert "payment" in response.json()["detail"].lower()


def test_cancel_with_refund_rejects_after_completed():
    oid = _create_paid_order()
    assert client.post(f"/orders/{oid}/submit").status_code == 200
    assert client.patch(f"/orders/{oid}/complete").status_code == 200
    response = client.post(f"/orders/{oid}/cancel-with-refund")
    assert response.status_code == 400
