import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem, Order

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
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
    menu_item_1 = MenuItem(id=1, food_item="Pizza", restaurant_id=1, price=10.0)
    menu_item_2 = MenuItem(id=2, food_item="Burger", restaurant_id=1, price=8.0)
    db.add(menu_item_1)
    db.add(menu_item_2)
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def existing_order():
    db = TestingSessionLocal()
    order = Order(
        order_id="test-order-1",
        customer_id=1,
        restaurant_id=1,
        order_value=20.0,
        food_item="Pizza"
    )
    db.add(order)
    db.commit()
    db.close()
    return {"order_id": "test-order-1"}


client = TestClient(app)


# --- create order ---

def test_create_order_success():
    response = client.post("/orders/create", json={
        "order_id": "order-abc",
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza", "Burger"],
        "order_value": 18.0
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Order created successfully"


# --- add item ---

def test_add_item_success(existing_order):
    response = client.post(f"/orders/{existing_order['order_id']}/add-item?food_item=Burger")
    assert response.status_code == 200
    assert "Burger" in response.json()["message"]


def test_add_item_order_not_found():
    response = client.post("/orders/nonexistent/add-item?food_item=Burger")
    assert response.status_code == 404


# --- remove item ---

def test_remove_item_success(existing_order):
    response = client.delete(f"/orders/{existing_order['order_id']}/remove-item?food_item=Pizza")
    assert response.status_code == 200
    assert "Pizza" in response.json()["message"]


def test_remove_item_not_found(existing_order):
    response = client.delete(f"/orders/{existing_order['order_id']}/remove-item?food_item=Sushi")
    assert response.status_code == 404


# --- update quantity ---

def test_update_quantity_increase(existing_order):
    response = client.patch(f"/orders/{existing_order['order_id']}/update-item?food_item=Pizza&quantity=3")
    assert response.status_code == 200

    # Confirm 3 rows exist in DB
    db = TestingSessionLocal()
    items = db.query(Order).filter(
        Order.order_id == existing_order["order_id"],
        Order.food_item == "Pizza"
    ).all()
    db.close()
    assert len(items) == 3


def test_update_quantity_decrease(existing_order):
    # First add more Pizza rows so we can decrease
    db = TestingSessionLocal()
    for _ in range(2):
        db.add(Order(order_id="test-order-1", customer_id=1, restaurant_id=1, order_value=20.0, food_item="Pizza"))
    db.commit()
    db.close()

    response = client.patch(f"/orders/{existing_order['order_id']}/update-item?food_item=Pizza&quantity=1")
    assert response.status_code == 200

    db = TestingSessionLocal()
    items = db.query(Order).filter(
        Order.order_id == existing_order["order_id"],
        Order.food_item == "Pizza"
    ).all()
    db.close()
    assert len(items) == 1


def test_update_quantity_zero_removes_item(existing_order):
    response = client.patch(f"/orders/{existing_order['order_id']}/update-item?food_item=Pizza&quantity=0")
    assert response.status_code == 200

    db = TestingSessionLocal()
    items = db.query(Order).filter(
        Order.order_id == existing_order["order_id"],
        Order.food_item == "Pizza"
    ).all()
    db.close()
    assert len(items) == 0


def test_update_item_not_found(existing_order):
    response = client.patch(f"/orders/{existing_order['order_id']}/update-item?food_item=Sushi&quantity=2")
    assert response.status_code == 404