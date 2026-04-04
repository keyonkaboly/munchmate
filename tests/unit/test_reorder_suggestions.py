"""Unit tests for reorder suggestion notification endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Order, Notification, Restaurant


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


def test_reorder_suggestion_success():
    """make sure customer with order history receives uggestion."""
    db = TestingSessionLocal()
    db.add(Restaurant(id=1, food_item="Burger Palace", location="Vancouver"))
    db.add(Order(combined_order_id="ORDER001", customer_id=1, restaurant_id=1, subtotal=15.0, food_item="Burger"))
    db.commit()
    db.close()

    response = client.get("/notifications/reorder-suggestions/1")
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["suggestions"][0]["notification_type"] == "reorder_suggestion"


def test_reorder_suggestion_no_history():
    """customer with no orders receives 404"""
    response = client.get("/notifications/reorder-suggestions/999")
    assert response.status_code == 404


def test_reorder_suggestion_message_content():
    """suggestion message check if it has restaurant/ food item."""
    db = TestingSessionLocal()
    db.add(Restaurant(id=2, food_item="Pizza Town", location="Vancouver"))
    db.add(Order(combined_order_id="ORDER002", customer_id=2, restaurant_id=2, subtotal=20.0, food_item="Margherita"))
    db.commit()
    db.close()

    response = client.get("/notifications/reorder-suggestions/2")
    message = response.json()["suggestions"][0]["message"]
    assert "Pizza Town" in message
    assert "Margherita" in message


def test_reorder_suggestion_saved_to_database():
    """CSee if Notification in the database is saved properly"""
    db = TestingSessionLocal()
    db.add(Restaurant(id=3, food_item="Sushi Spot", location="Vancouver"))
    db.add(Order(combined_order_id="ORDER003", customer_id=3, restaurant_id=3, subtotal=30.0, food_item="Salmon Roll"))
    db.commit()
    db.close()

    client.get("/notifications/reorder-suggestions/3")

    db = TestingSessionLocal()
    saved = db.query(Notification).filter(Notification.customer_id == 3, Notification.notification_type == "reorder_suggestion").first()
    db.close()
    assert saved is not None
    assert "Sushi Spot" in saved.message