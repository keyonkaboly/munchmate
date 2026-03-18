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


def test_login_success():
    register_payload = {
        "email": "loginuser@example.com",
        "username": "loginuser",
        "password": "password123"
    }

    register_response = client.post("/auth/register?role=customer", json=register_payload)
    assert register_response.status_code == 200

    login_payload = {
        "email": "loginuser@example.com",
        "password": "password123"
    }

    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["user"]["email"] == "loginuser@example.com"
    assert data["user"]["username"] == "loginuser"


def test_login_invalid_password():
    register_payload = {
        "email": "wrongpass@example.com",
        "username": "wrongpass",
        "password": "password123"
    }

    register_response = client.post("/auth/register?role=customer", json=register_payload)
    assert register_response.status_code == 200

    login_payload = {
        "email": "wrongpass@example.com",
        "password": "wrongpassword"
    }

    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_login_nonexistent_email():
    login_payload = {
        "email": "nouser@example.com",
        "password": "password123"
    }

    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"