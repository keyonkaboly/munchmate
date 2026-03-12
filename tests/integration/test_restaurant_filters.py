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
    assert len(data) == 1
    assert data[0]["name"] == "Halal Place"

# filtering by vegetarian 
def test_filter_by_vegetarian():
    response = client.get("/restaurants/?is_vegetarian=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Veggie Place"

# no filters returns all restaurants
def test_no_filter_returns_all():
    response = client.get("/restaurants/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

# filter with no matches returns the correct message
def test_filter_no_results():
    response = client.get("/restaurants/?is_halal=true&is_vegetarian=true")
    assert response.status_code == 200
    assert response.json() == {"message": "No restaurants found"}