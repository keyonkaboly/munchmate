import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem


TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

"""redirecting database calls to the test database during tests"""
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

"""prepares and cleans up test data before and after each test"""
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    restaurant = Restaurant(id=1, location="City_3", food_item="Pizza")
    second_restaurant = Restaurant(id=2, location="City_8", food_item="Burger")
    db.add(restaurant)
    db.add(second_restaurant)
    menu_item = MenuItem(id=1, food_item="Pizza", restaurant_id=1, price=10)
    db.add(menu_item)
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


"""Verifies that fetching a restaurant returns the correct JSON format"""
def test_get_restaurant_returns_correct_format():
    response = client.get("/restaurants/1")
    assert response.status_code == 200
    json_data = response.json()
    assert "id" in json_data
    assert json_data["id"] == 1
