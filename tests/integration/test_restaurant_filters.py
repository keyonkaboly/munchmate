import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant

# Use a separate test database so we don't touch real data
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# redirecting database calls to the test database during tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# prepares and cleaning up test data before and after each test
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(Restaurant(id=1, name="Halal Place", is_halal=True, is_vegetarian=False))
    db.add(Restaurant(id=2, name="Veggie Place", is_halal=False, is_vegetarian=True))
    db.add(Restaurant(id=3, name="Regular Place", is_halal=False, is_vegetarian=False))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)

# simulating real HTTP requests to the API during tests
client = TestClient(app)

# filtering by halal 
def test_filter_by_halal():
    response = client.get("/restaurants/?is_halal=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Halal Place"

# filtering by vegetarian 
def test_filter_by_vegetarian():
    response = client.get("/restaurants/?is_vegetarian=true")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Veggie Place"

# no filters returns all restaurants
def test_no_filter_returns_all():
    response = client.get("/restaurants/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3

# filter with no matches returns the correct message
def test_filter_no_results():
    response = client.get("/restaurants/?is_halal=true&is_vegetarian=true")
    assert response.status_code == 200
    assert response.json() == {"message": "No restaurants found"}

"""Ensure the first page of restaurant returns 20 items, has page num 1, and includes a total of 2 pages."""
def test_pagination_first_page():
    db = TestingSessionLocal()
    for i in range(4, 26):
        db.add(Restaurant(id=i, name=f"Restaurant {i}", is_halal=False, is_vegetarian=False))
    db.commit()
    db.close()

    data = client.get("/restaurants/?page=1&page_size=20").json()
    assert len(data["items"]) == 20
    assert data["total"] == 25
    assert data["page"] == 1
    assert data["total_pages"] == 2

"""Ensure the second page of restaurants endpoint returns remaining items from 25 items from prev test.
Page 2 should only contain leftover results. Check if page num is 2 and item num is 5 (25-20)"""
def test_pagination_second_page():
    db = TestingSessionLocal()
    for i in range(4, 26):
        db.add(Restaurant(id=i, name=f"Restaurant {i}", is_halal=False, is_vegetarian=False))
    db.commit()
    db.close()

    data = client.get("/restaurants/?page=2&page_size=20").json()
    assert len(data["items"]) == 5
    assert data["page"] == 2