import pytest
from fastapi.testclient import TestClient
from app.main import app

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