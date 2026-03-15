"""Unit tests for payment simulation endpoint."""
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


def test_successful_payment():
    """Check that a valid payment returns success."""
    db = TestingSessionLocal()
    db.add(Order(order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.commit()
    db.close()

    response = client.post("/payments/simulate?order_id=TEST001&amount=50")
    assert response.status_code == 200
    assert response.json()["payment_status"] == "success"


def test_invalid_order_id():
    """Check that a non-existent order returns 404."""
    response = client.post("/payments/simulate?order_id=FAKE999&amount=50")
    assert response.status_code == 404


def test_invalid_amount():
    """Check that a non-positive amount returns 400."""
    db = TestingSessionLocal()
    db.add(Order(order_id="TEST001", customer_id=1, restaurant_id=1, subtotal=50.0))
    db.commit()
    db.close()

    response = client.post("/payments/simulate?order_id=TEST001&amount=0")
    assert response.status_code == 400