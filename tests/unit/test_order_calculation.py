import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.application.services.pricing_service import calculate_order_total
from app.application.services.pricing_service import calculate_tax
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Order, Restaurant, MenuItem
from fastapi.testclient import TestClient

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

def test_calculate_order_total():
    result = calculate_order_total(22.79)

    assert result == {"subtotal": 22.79, "tax": 2.73, "delivery_cost": 5.00, "total_cost": 30.52}

def test_calculate_tax():
    result = calculate_tax(22.79)
    assert result == 2.73
    
def test_order_not_found():
    response = client.post(f"/checkout/calculate", json = {"order_id": "Str1ng"})
    assert response.status_code == 404

def test_checkout_calculate_success():
    db = TestingSessionLocal()
    order = Order(order_id="Str1ng", customer_id=1, restaurant_id=1, subtotal=22.79)

    db.add(order)
    db.commit()
    db.close()

    result = calculate_order_total(22.79)
    response = client.post("/checkout/calculate", json={"order_id":"Str1ng"})

    assert response.status_code == 200
    assert response.json() == {"order_id":"Str1ng", "subtotal":result["subtotal"], "tax":result["tax"], "delivery_cost":result["delivery_cost"],"total_cost":result["total_cost"]}

def test_checkout_calculate_combined_order_dynamic_total():
    db = TestingSessionLocal()
    db.add(Restaurant(id=1))
    db.add(MenuItem(restaurant_id=1, food_item="Whole Pizza", price=32.0))
    db.add(MenuItem(restaurant_id=1, food_item="7-11 Soda", price=30.0))
    db.add(Order(combined_order_id="uuid-order-id-93", restaurant_id=1, food_item="Whole Pizza"))
    db.add(Order(combined_order_id="uuid-order-id-93", customer_id=1, restaurant_id=1, food_item="7-11 Soda"))
    db.commit()
    db.close()

    response = client.post("/checkout/calculate", json={"order_id": "uuid-order-id-93"})

    assert response.status_code == 200
    assert response.json() == {"order_id": "uuid-order-id-93", "subtotal": 62.0, "tax": 7.44, "delivery_cost": 5.0, "total_cost": 74.44}
