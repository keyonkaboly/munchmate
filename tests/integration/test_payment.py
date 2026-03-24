import pytest
from fastapi.testclient import TestClient
from app.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
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

    db = TestingSessionLocal()
    restaurant = Restaurant(id=1, location="123 Test St")
    db.add(restaurant)

    menu_item = MenuItem(id=1, food_item="Pizza", restaurant_id=1)
    db.add(menu_item)

    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_payment_success():
    order_response = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"]
    })
    combined_order_id = order_response.json()["combined_order_id"]
    client.post(f"/checkout/orders/{combined_order_id}/place")
    response = client.post("/payments/", json={
        "order_id": combined_order_id,
        "total_cost": 25.99,
        "card_number": "1234567890001234"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Payment successful"

def test_payment_declined_card():
    order_response = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"]
    })
    combined_order_id = order_response.json()["combined_order_id"]
    client.post(f"/checkout/orders/{combined_order_id}/place")
    response = client.post("/payments/", json={
        "order_id": combined_order_id,
        "total_cost": 25.99,
        "card_number": "1234567890000000"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert data["message"] == "Payment failed: card declined"


def test_payment_simulation_only():
    order_response = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"]
    })
    combined_order_id = order_response.json()["combined_order_id"]
    client.post(f"/checkout/orders/{combined_order_id}/place")
    response = client.post("/payments/", json={
        "order_id": combined_order_id,
        "total_cost": 50.00,
        "card_number": "9999999999999999"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_checkout_success():
    order_response = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"]
    })
    combined_order_id = order_response.json()["combined_order_id"]
    client.post(f"/checkout/orders/{combined_order_id}/place")
    response = client.post("/payments/checkout", json={
        "order_id": combined_order_id,
        "total_cost": 25.99,
        "card_number": "1234567890001234"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["message"] == "Payment successful"

def test_checkout_order_not_found():
    response = client.post("/payments/checkout", json={
        "order_id": "Str1ng",
        "total_cost": 25.99,
        "card_number": "1234567890001234"
    })
    assert response.status_code == 404

def test_checkout_accepts_valid_input():
    order_response = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"]
    })
    combined_order_id = order_response.json()["combined_order_id"]
    client.post(f"/checkout/orders/{combined_order_id}/place")
    response = client.post("/payments/checkout", json={
        "order_id": combined_order_id,
        "total_cost": 50.00,
        "card_number": "9999999999999999"
    })
    assert response.status_code == 200
    assert response.json()["success"] == True