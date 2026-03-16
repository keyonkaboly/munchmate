import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base

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

# Verifies successful payment with valid card and amount
def test_payment_success():
    response = client.post("/payments/", json={
        "order_id": 1,
        "total_price": 25.99,
        "card_number": "1234567890001234"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Payment successful"

# Verifies payment fails with declined card ending in 0000
def test_payment_declined_card():
    response = client.post("/payments/", json={
        "order_id": 2,
        "total_price": 25.99,
        "card_number": "1234567890000000"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Payment failed: card declined"

# Verifies payment fails with invalid order amount
def test_payment_invalid_amount():
    response = client.post("/payments/", json={
        "order_id": 3,
        "total_price": 0,
        "card_number": "1234567890001234"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Payment failed: invalid order amount"

# Verifies no real payment gateway is used
def test_payment_simulation_only():
    response = client.post("/payments/", json={
        "order_id": 4,
        "total_price": 50.00,
        "card_number": "9999999999999999"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True

# Verifies checkout triggers simulated payment for existing order
def test_checkout_success():
    # first create an order
    order_response = client.post("/orders/", json={
        "delivery_method": "Bike",
        "delivery_distance": 2.5,
        "route_taken": "Route_1",
        "route_type": "Bike-friendly",
        "route_efficiency": 0.85
    })
    order_id = order_response.json()["order_id"]
    response = client.post("/payments/checkout", json={
        "order_id": order_id,
        "total_price": 25.99,
        "card_number": "1234567890001234"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Payment successful"

# Verifies checkout fails for non-existent order
def test_checkout_order_not_found():
    response = client.post("/payments/checkout", json={
        "order_id": 999,
        "total_price": 25.99,
        "card_number": "1234567890001234"
    })
    assert response.status_code == 404

# Verifies checkout accepts valid simulated input formats
def test_checkout_accepts_valid_input():
    order_response = client.post("/orders/", json={
        "delivery_method": "Car",
        "delivery_distance": 3.0,
        "route_taken": "Route_2",
        "route_type": "Car-only",
        "route_efficiency": 0.75
    })
    order_id = order_response.json()["order_id"]
    response = client.post("/payments/checkout", json={
        "order_id": order_id,
        "total_price": 50.00,
        "card_number": "9999999999999999"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True