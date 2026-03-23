import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Order

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

"""delivery info is saved and can be retrieved"""
def test_delivery_info_saved_and_retrievable():
    post_response = client.post("/orders/", json={
        "order_id": "Str1ng",
        "restaurant_id": 1,
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

"""delivery info is saved automatically when order is placed"""
def test_delivery_info_saved_automatically_on_order_placement():
    response = client.post("/orders/", json={
        "order_id": "Str1ng",
        "restaurant_id": 1,
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

"""delivery data remains accessible for lifetime of order"""
def test_delivery_info_remains_accessible():
    post_response = client.post("/orders/", json={
        "order_id": "Str1ng",
        "restaurant_id": 1,
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

"""Verifies non-existent order returns 404"""
def test_get_nonexistent_order_returns_404():
    response = client.get("/orders/999")
    assert response.status_code == 404