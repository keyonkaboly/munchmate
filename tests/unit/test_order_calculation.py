import pytest
from sqlalchemy.orm import sessionmaker
from app.application.services.pricing_service import calculate_order_total
from app.application.services.pricing_service import calculate_tax
from app.infrastructure.database.models import Order
from conftest import TestingSessionLocal, client as client_fixture


@pytest.fixture(autouse=True)
def clean_orders():
    # clean before each test
    db = TestingSessionLocal()
    db.query(Order).delete()
    db.commit()
    db.close()
    yield
   
    db = TestingSessionLocal()
    db.query(Order).delete()
    db.commit()
    db.close()


def test_calculate_order_total():
    result = calculate_order_total(22.79)
    assert result == {"subtotal": 22.79, "tax": 2.73, "delivery_cost": 5.00, "total_cost": 30.52}

def test_calculate_tax():
    result = calculate_tax(22.79)
    assert result == 2.73

def test_order_not_found(client):
    response = client.post("/checkout/calculate", json={"order_id": "Str1ng"})
    assert response.status_code == 404

def test_checkout_calculate_success(client):
    db = TestingSessionLocal()
    order = Order(order_id="Str1ng", customer_id=1, restaurant_id=1, subtotal=22.79)
    db.add(order)
    db.commit()
    db.close()

    result = calculate_order_total(22.79)
    response = client.post("/checkout/calculate", json={"order_id": "Str1ng"})

    assert response.status_code == 200
    assert response.json() == {
        "order_id": "Str1ng",
        "subtotal": result["subtotal"],
        "tax": result["tax"],
        "delivery_cost": result["delivery_cost"],
        "total_cost": result["total_cost"]
    }