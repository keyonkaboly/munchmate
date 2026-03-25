"""Unit tests for restaurant incoming order notification endpoints."""
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


def test_incoming_order_notification_success():
    """Check that a notification is sent to restaurant owner when order is placed."""
    db = TestingSessionLocal()
    db.add(Order(combined_order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.commit()
    db.close()

    response = client.post("/notifications/incoming-order?order_id=TEST001&restaurant_id=1")
    assert response.status_code == 200
    assert response.json()["notification_type"] == "incoming_order"


def test_incoming_order_notification_order_not_found():
    """Check that a notification for a non-existent order returns 404."""
    response = client.post("/notifications/incoming-order?order_id=FAKE999&restaurant_id=1")
    assert response.status_code == 404


def test_incoming_order_notification_correct_restaurant():
    """Check that the notification contains the correct restaurant ID."""
    db = TestingSessionLocal()
    db.add(Order(combined_order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.commit()
    db.close()

    response = client.post("/notifications/incoming-order?order_id=TEST001&restaurant_id=1")
    assert response.status_code == 200
    assert response.json()["restaurant_id"] == 1


def test_get_restaurant_notifications_success():
    """Check that restaurant notification list returns correct notifications."""
    db = TestingSessionLocal()
    db.add(Order(combined_order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.add(Notification(customer_id=1, order_id="TEST001", message="New order received", notification_type="incoming_order"))
    db.commit()
    db.close()

    response = client.get("/notifications/restaurant/1")
    assert response.status_code == 200
    assert len(response.json()["notifications"]) == 1


def test_get_restaurant_notifications_empty():
    """Check that empty list is returned for restaurant with no notifications."""
    response = client.get("/notifications/restaurant/999")
    assert response.status_code == 200
    assert response.json()["notifications"] == []