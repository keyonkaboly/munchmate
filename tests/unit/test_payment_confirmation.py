"""Unit tests for payment confirmation endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Order, Payment


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


def test_payment_confirmation_success():
    """Check that a confirmed payment returns the correct message."""
    db = TestingSessionLocal()
    db.add(Order(order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.add(Payment(order_id="TEST001", status="success", amount=50))
    db.commit()
    db.close()

    response = client.get("/payments/confirmation/TEST001")
    assert response.status_code == 200
    assert response.json()["status"] == "Payment Successful"
    assert response.json()["message"] == "Payment confirmed"


def test_payment_confirmation_not_found():
    """Check that a non-existent payment confirmation returns 404."""
    response = client.get("/payments/confirmation/FAKE999")
    assert response.status_code == 404


def test_payment_confirmation_failed_payment():
    """Check that a failed payment does not return confirmation."""
    db = TestingSessionLocal()
    db.add(Order(order_id="TEST002", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.add(Payment(order_id="TEST002", status="failed", amount=0))
    db.commit()
    db.close()

    response = client.get("/payments/confirmation/TEST002")
    assert response.status_code == 404