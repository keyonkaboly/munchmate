import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem

TEST_DATABASE_URL = "sqlite:///./test_create.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    db.add(Restaurant(id=1))
    db.add(MenuItem(id=1, restaurant_id=1, food_item="Pizza", price=10))
    db.add(MenuItem(id=2, restaurant_id=1, food_item="Burger", price=8))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def test_create_order_success():
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza", "Burger"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "combined_order_id" in data
    assert data["count"] == 2


def test_create_order_empty():
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": []
    })
    assert res.status_code == 400


def test_create_invalid_item():
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Sushi"]
    })
    assert res.status_code == 404