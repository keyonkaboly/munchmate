import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.presentation.api.v1.authentication import router_auth
from app.infrastructure.database.database import Base, engine

app = FastAPI()
app.include_router(router_auth)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_customer_success():
    payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "password123"
    }

    response = client.post("/auth/register?role=customer", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["username"] == payload["username"]
    assert data["role"] == "customer"


def test_register_restaurant_manager_success():
    payload = {
        "email": "owner@example.com",
        "username": "owneruser",
        "password": "password123"
    }

    response = client.post("/auth/register?role=restaurant_manager", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "restaurant_manager"


def test_register_invalid_email():
    payload = {
        "email": "not_an_email",
        "username": "testuser",
        "password": "password123"
    }

    response = client.post("/auth/register?role=customer", json=payload)
    assert response.status_code == 422


def test_register_missing_role():
    payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "password123"
    }

    response = client.post("/auth/register", json=payload)
    assert response.status_code == 422


def test_register_invalid_role():
    payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "password123"
    }

    response = client.post("/auth/register?role=admin", json=payload)
    assert response.status_code == 400


def test_register_duplicate_email():
    payload = {
        "email": "duplicate@example.com",
        "username": "testuser",
        "password": "password123"
    }

    response = client.post("/auth/register?role=customer", json=payload)
    assert response.status_code == 200

    payload2 = {
        "email": "duplicate@example.com",
        "username": "otheruser",
        "password": "password123"
    }

    response = client.post("/auth/register?role=customer", json=payload2)
    assert response.status_code == 400