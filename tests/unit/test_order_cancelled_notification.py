"""Unit tests for order cancelled notification endpoint."""
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


def test_order_cancelled_notification_success():
    """Check that a notification is sent when an order is cancelled."""
    db = TestingSessionLocal()
    db.add(Order(combined_order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.commit()
    db.close()

    response = client.post("/notifications/order-cancelled?order_id=TEST001&customer_id=1")
    assert response.status_code == 200
    assert response.json()["notification_type"] == "order_cancelled"


def test_order_cancelled_notification_order_not_found():
    """Check that a notification for a non-existent order returns 404."""
    response = client.post("/notifications/order-cancelled?order_id=FAKE999&customer_id=1")
    assert response.status_code == 404


def test_order_cancelled_notification_correct_customer():
    """Check that the cancellation notification is sent to the correct customer."""
    db = TestingSessionLocal()
    db.add(Order(combined_order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.commit()
    db.close()

    response = client.post("/notifications/order-cancelled?order_id=TEST001&customer_id=1")
    assert response.status_code == 200
    assert response.json()["customer_id"] == 1