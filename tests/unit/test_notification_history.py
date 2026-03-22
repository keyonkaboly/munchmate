"""Unit tests for notification history endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Order, Notification


TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    """Override the database dependency to use the test database."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_notification_history_success():
    """Check that notification history is returned for a valid customer."""
    db = TestingSessionLocal()
    db.add(Order(order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.commit()
    db.add(Notification(customer_id=1, order_id="TEST001", message="Order confirmed", notification_type="order_created"))
    db.commit()
    db.add(Notification(customer_id=1, order_id="TEST001", message="Order on the way", notification_type="delivery_status"))
    db.commit()
    db.close()
    response = client.get("/notifications/history/1")
    assert response.status_code == 200
    assert len(response.json()["notifications"]) == 2


def test_notification_history_empty():
    """Check that empty list is returned for customer with no notifications."""
    response = client.get("/notifications/history/999")
    assert response.status_code == 200
    assert response.json()["notifications"] == []


def test_notification_history_correct_customer():
    """Check that only notifications for the correct customer are returned."""
    db = TestingSessionLocal()
    db.add(Order(order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.add(Order(order_id="TEST002", customer_id=2, restaurant_id=1, subtotal=30.0))
    db.add(Notification(customer_id=1, order_id="TEST001", message="Order confirmed", notification_type="order_created"))
    db.add(Notification(customer_id=2, order_id="TEST002", message="Order confirmed", notification_type="order_created"))
    db.commit()
    db.close()

    response = client.get("/notifications/history/1")
    assert response.status_code == 200
    assert len(response.json()["notifications"]) == 1
    assert response.json()["notifications"][0]["order_id"] == "TEST001"