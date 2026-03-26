import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlalchemy.orm import Session

from app.infrastructure.database.database import Base, engine, get_db
from app.infrastructure.database.models import Customer, Restaurant, Order
from app.presentation.api.v1.restaurants import router as restaurant_router
from app.application.services.authentication_service import get_current_user


app = FastAPI()
app.include_router(restaurant_router)
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def override_current_user(user):
    def _override():
        return user
    return _override



"""setup test data"""
def create_test_data(db: Session):
    r1 = Restaurant(id=1, location="Test1", food_item="Pizza")
    r2 = Restaurant(id=2, location="Test2", food_item="Burger")

    db.add_all([r1, r2])
    db.commit()

    order1 = Order(order_id="o1", restaurant_id=1)
    order2 = Order(order_id="o2", restaurant_id=1)
    order3 = Order(order_id="o3", restaurant_id=2)

    db.add_all([order1, order2, order3])
    db.commit()

    return r1, r2



"""manager can access own restaurant"""
def test_manager_can_access_own_orders():
    db = next(get_db())
    create_test_data(db)

    manager = Customer(
        id=1,
        email="manager@test.com",
        username="manager",
        password_hash="hashed",
        user_type="restaurant_manager",
        restaurant_manager_restaurant_id=1
    )

    app.dependency_overrides[get_current_user] = override_current_user(manager)


    response = client.get("/restaurants/1/orders")
    assert response.status_code == 404
