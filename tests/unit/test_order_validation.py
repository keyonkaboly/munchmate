import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base

from app.infrastructure.database.models import Restaurant, MenuItem, Order, Customer

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
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    db.add(Restaurant(id=1, location="123 Test St"))
    db.add(MenuItem(food_item="Pizza", restaurant_id=1, price=10.0))
    db.add(MenuItem(food_item="Burger", restaurant_id=1, price=8.0))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


def test_order_valid_items_are_accepted():
    """Valid menu items -> order is created successfully."""
    response = client.post("/orders/create", json={
        "order_id": "order-1",
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza", "Burger"],
        "order_value": 18.0
    })
    assert response.status_code == 200
    assert len(response.json()["order_ids"]) == 2


def test_order_invalid_item_is_rejected():
    """Item not on the menu -> 404 with the item name in the error."""
    response = client.post("/orders/create", json={
        "order_id": "order-2",
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Sushi"],
        "order_value": 12.0
    })
    assert response.status_code == 404
    assert "Sushi" in response.json()["detail"]