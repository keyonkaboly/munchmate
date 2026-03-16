"""Unit tests for payment simulation endpoint."""
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
    response = client.post("/payments/", json={
        "order_id": 1,
        "total_price": 50.0,
        "card_number": "4111111111111111"
    })
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_declined_card():
    """Check that a card ending in 0000 is declined."""
    response = client.post("/payments/", json={
        "order_id": 1,
        "total_price": 50.0,
        "card_number": "4111111110000"
    })
    assert response.status_code == 200
    assert response.json()["success"] is False


def test_invalid_amount():
    """Check that a non-positive amount returns failed payment."""
    response = client.post("/payments/", json={
        "order_id": 1,
        "total_price": 0.0,
        "card_number": "4111111111111111"
    })
    assert response.status_code == 200
    assert response.json()["success"] is False