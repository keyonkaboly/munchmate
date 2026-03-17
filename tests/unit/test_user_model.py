import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.presentation.api.v1.users import router_user
from app.infrastructure.database.database import Base, engine

app = FastAPI()
app.include_router(router_user)

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


def test_create_user_success():
    user_payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "securepassword"
    }

    response = client.post("/users/", json=user_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_payload["email"]
    assert data["username"] == user_payload["username"]
    assert "password" not in data


def test_create_user_email_invalid():
    user_payload = {
        "email": "not_an_email",
        "username": "testuser",
        "password": "securepassword"
    }

    response = client.post("/users/", json=user_payload)
    assert response.status_code == 422


def test_create_user_short_password():
    user_payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "123"
    }

    response = client.post("/users/", json=user_payload)
    assert response.status_code == 422


def test_create_user_duplicate_email():
    user_payload = {
        "email": "duplicate@example.com",
        "username": "testuser",
        "password": "123456"
    }

    response = client.post("/users/", json=user_payload)
    assert response.status_code == 200

    response = client.post("/users/", json=user_payload)
    assert response.status_code == 400