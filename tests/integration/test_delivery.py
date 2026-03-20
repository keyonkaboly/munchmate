import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Order, Restaurant, MenuItem, Customer

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
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(Customer(id="9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"))
    db.add(Restaurant(id=1, cuisine_type="Italian"))
    db.add(MenuItem(restaurant_id=1, food_item="Pizza"))
    # seeded dataset row with delivery info
    db.add(Order(
        order_id="seed-1",
        restaurant_id=1,
        food_item="Pizza",
        delivery_method="Bike",
        delivery_distance=2.5,
        delivery_delay=5.0,
        route_taken="Route_1",
        route_type="Bike-friendly",
        route_efficiency=0.85,
        status="seeded",
        subtotal=10.0, tax=1.2, delivery_cost=5.0, total_cost=16.2
    ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)


def test_delivery_info_saved_and_retrievable():
    """Delivery info is assigned from seeded data when order is created."""
    response = client.post("/orders/create", json={
        "customer_id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        "restaurant_id": 1,
        "food_items": ["Pizza"],
        "order_value": 12.5
    })
    assert response.status_code == 200
    order_id = response.json()["order_id"]

    db = TestingSessionLocal()
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.status == "draft"
    ).first()
    assert order.delivery_method == "Bike"
    assert order.delivery_distance == 2.5
    assert order.route_taken == "Route_1"
    db.close()


def test_delivery_info_saved_automatically_on_order_placement():
    """Delivery info is automatically stamped onto the order on creation."""
    response = client.post("/orders/create", json={
        "customer_id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        "restaurant_id": 1,
        "food_items": ["Pizza"],
        "order_value": 12.5
    })
    assert response.status_code == 200
    order_id = response.json()["order_id"]
    assert order_id is not None

    db = TestingSessionLocal()
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.status == "draft"
    ).first()
    assert order.delivery_method is not None
    db.close()


def test_delivery_info_remains_accessible():
    """Delivery info stays on the order after creation."""
    response = client.post("/orders/create", json={
        "customer_id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        "restaurant_id": 1,
        "food_items": ["Pizza"],
        "order_value": 12.5
    })
    assert response.status_code == 200
    order_id = response.json()["order_id"]

    db = TestingSessionLocal()
    order = db.query(Order).filter(
        Order.order_id == order_id,
        Order.status == "draft"
    ).first()
    assert order.order_id == order_id
    assert order.delivery_method is not None
    db.close()


def test_get_nonexistent_order_returns_404():
    """Non-existent order returns 404."""
    response = client.get("/orders/999")
    assert response.status_code == 404