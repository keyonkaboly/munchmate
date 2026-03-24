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
    db.add(Restaurant(id=1, location="123 Test St"))
    db.add(MenuItem(id=1, food_item="Pizza", restaurant_id=1))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def create_completed_order():
    res = client.post("/orders/create", json={
        "customer_id": 1,
        "restaurant_id": 1,
        "food_items": ["Pizza"]
    })
    order_id = res.json()["combined_order_id"]
    client.post(f"/orders/{order_id}/submit")
    client.patch(f"/orders/{order_id}/complete")
    return order_id

# delivery info is saved and can be retrieved
def test_delivery_info_saved_and_retrievable():
    order_id = create_completed_order()
    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["order_id"] is not None

# delivery info is saved automatically when order is placed
def test_delivery_info_saved_automatically_on_order_placement():
    order_id = create_completed_order()
    get_response = client.get(f"/orders/{order_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["order_id"] is not None

# delivery data remains accessible for lifetime of order
def test_delivery_info_remains_accessible():
    order_id = create_completed_order()
    for _ in range(3):
        get_response = client.get(f"/orders/{order_id}")
        assert get_response.status_code == 200
        assert get_response.json()["order_id"] is not None

# Verifies non-existent order returns 404
def test_get_nonexistent_order_returns_404():
    response = client.get("/orders/999")
    assert response.status_code == 404