import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.infrastructure.database.database import get_db
from app.infrastructure.database.models import Base, Restaurant, MenuItem, Customer 

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
    db.add(Customer(id="9c6dbfcb-72c5-4cc4-9f76-29200f0efda7"))
    db.add(Restaurant(id=1, cuisine_type="Italian"))
    db.add(MenuItem(restaurant_id=1, food_item="Pizza"))
    db.add(MenuItem(restaurant_id=1, food_item="Burger"))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


def test_submit_valid_order():
    create_response = client.post("/orders/create", json={
        "customer_id": "9c6dbfcb-72c5-4cc4-9f76-29200f0efda7",
        "restaurant_id": 1,
        "food_items": ["Pizza"],
        "order_value": 12.5
    })
    assert create_response.status_code == 200
    order_id = create_response.json()["order_id"]

    response = client.post(f"/orders/{order_id}/submit")
    assert response.status_code == 200
    assert "submitted" in response.json()["message"].lower()


def test_submit_invalid_order():
    response = client.post("/orders/badorder/submit")
    assert response.status_code in [400, 404]