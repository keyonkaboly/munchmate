import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem

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
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    restaurant = Restaurant(id=1, location="123 Test St")
    db.add(restaurant)
    menu_item = MenuItem(id=1, food_item="Pizza", restaurant_id=1)
    db.add(menu_item)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_order_with_items():
    response = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "items": [{"menu_item_id": 1, "quantity": 2}]
    })
    assert response.status_code == 200
    assert response.json()["order_id"] is not None


def test_create_order_invalid_menu_item():
    response = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "items": [{"menu_item_id": 999, "quantity": 2}]
    })
    assert response.status_code == 404