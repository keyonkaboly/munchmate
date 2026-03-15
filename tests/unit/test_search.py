"""Unit tests for the global restaurant search endpoint."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant


TEST_DATABASE_URL = "sqlite:///./test_search.db"
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
    """Create tables and seed test data before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Restaurant(id=1, name="Pizza Palace", category="Italian"))
    db.add(Restaurant(id=2, name="Burger Barn", category="American"))
    db.add(Restaurant(id=3, name="Sushi Spot", category="Japanese"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_search_by_name():
    """Check that searching by restaurant name returns correct results."""
    response = client.get("/search/restaurants?query=Pizza")
    assert response.status_code == 200
    assert response.json()["results"][0]["name"] == "Pizza Palace"


def test_search_by_category():
    """Check that searching by category returns correct results."""
    response = client.get("/search/restaurants?query=American")
    assert response.status_code == 200
    assert response.json()["results"][0]["category"] == "American"


def test_search_no_results():
    """Check that searching for something that does not exist returns empty list."""
    response = client.get("/search/restaurants?query=XYZ999")
    assert response.status_code == 200
    assert response.json()["results"] == []


def test_search_invalid_input():
    """Check that invalid characters in search query return 400 error."""
    response = client.get("/search/restaurants?query=@@@")
    assert response.status_code == 400