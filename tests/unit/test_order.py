from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


def test_create_order():

    response = client.post(
        "/orders/",
        json={
            "customer_id": 1,
            "restaurant_id": 1,
            "items": [
                {"menu_item_id": 1, "quantity": 2}
            ]
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "order_id" in data
   