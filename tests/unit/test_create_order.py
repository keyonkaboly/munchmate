import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Order, Restaurant, MenuItem

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(Restaurant(id=1, cuisine_type="Italian"))
    db.add(MenuItem(restaurant_id=1, food_item="Pizza"))
    db.add(MenuItem(restaurant_id=1, food_item="Burger"))
    db.commit()
    db.close()

    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)

def test_create_order_with_single_food_item():
    response = client.post("/orders/create", json={
        "order_id": "order123_pizza",
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"],
        "order_value": 12.5
    })
    assert response.status_code == 200
    json_data = response.json()
    assert "order_ids" in json_data
    assert json_data["order_ids"] == ["order123_pizza"]


def test_create_order_with_multiple_food_items():
    response1 = client.post("/orders/create", json={
        "order_id": "order123_pizza",
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"],
        "order_value": 12.5
    })
    assert response1.status_code == 200
    json1 = response1.json()
    assert "order_ids" in json1
    assert json1["order_ids"] == ["order123_pizza"]

    response2 = client.post("/orders/create", json={
        "order_id": "order123_burger",
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Burger"],
        "order_value": 12.5
    })
    assert response2.status_code == 200
    json2 = response2.json()
    assert "order_ids" in json2
    assert json2["order_ids"] == ["order123_burger"]


def test_create_order_with_no_food_items():
    response = client.post("/orders/create", json={
        "order_id": "order_empty",
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": [],
        "order_value": 0.0
    })
    assert response.status_code == 200
    json_data = response.json()
    assert json_data.get("row_ids") == [] or json_data.get("order_ids") == []