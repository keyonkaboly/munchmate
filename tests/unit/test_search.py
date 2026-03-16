"""Unit tests for the global restaurant search endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant


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
    db = TestingSessionLocal()
    db.add(Restaurant(id=1, location="City_1", food_item="Pizza", cuisine_type="Italian", is_halal=False, is_vegetarian=False))
    db.add(Restaurant(id=2, location="City_2", food_item="Sushi", cuisine_type="Japanese", is_halal=False, is_vegetarian=False))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_search_by_valid_restaurant_id():
    """Check that searching by valid restaurant ID returns correct result."""
    response = client.get("/search/restaurants?restaurant_id=1")
    assert response.status_code == 200
    assert response.json()["results"][0]["restaurant_id"] == 1


def test_search_by_invalid_restaurant_id():
    """Check that searching for non-existent restaurant ID returns empty list."""
    response = client.get("/search/restaurants?restaurant_id=999")
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_search_by_negative_id():
    """Check that a negative restaurant ID returns 400 error."""
    response = client.get("/search/restaurants?restaurant_id=-1")
    assert response.status_code == 400