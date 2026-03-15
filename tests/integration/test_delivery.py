import pytest
from app.infrastructure.database.models import Order
from conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def clean_orders():
    db = TestingSessionLocal()
    db.query(Order).delete()
    db.commit()
    db.close()
    yield
    db = TestingSessionLocal()
    db.query(Order).delete()
    db.commit()
    db.close()


def test_delivery_info_saved_and_retrievable(client):
    post_response = client.post("/orders/", json={
        "delivery_method": "Bike",
        "delivery_distance": 2.5,
        "delivery_time": "2024-01-31",
        "delivery_time_actual": 30.0,
        "delivery_delay": 5.0,
        "route_taken": "Route_1",
        "route_type": "Bike-friendly",
        "route_efficiency": 0.85
    })
    assert post_response.status_code == 200
    order_id = post_response.json()["order_id"]
    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["delivery_method"] == "Bike"
    assert data["delivery_distance"] == 2.5
    assert data["route_taken"] == "Route_1"


def test_delivery_info_saved_automatically_on_order_placement(client):
    response = client.post("/orders/", json={
        "delivery_method": "Car",
        "delivery_distance": 5.0,
        "route_taken": "Route_2",
        "route_type": "Car-only",
        "route_efficiency": 0.75
    })
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] is not None
    assert data["delivery_method"] == "Car"


def test_delivery_info_remains_accessible(client):
    post_response = client.post("/orders/", json={
        "delivery_method": "Walk",
        "delivery_distance": 1.0,
        "route_taken": "Route_3",
        "route_type": "Bike-friendly",
        "route_efficiency": 0.90
    })
    order_id = post_response.json()["order_id"]
    for _ in range(3):
        get_response = client.get(f"/orders/{order_id}")
        assert get_response.status_code == 200
        assert get_response.json()["order_id"] == order_id


def test_get_nonexistent_order_returns_404(client):
    response = client.get("/orders/999")
    assert response.status_code == 404