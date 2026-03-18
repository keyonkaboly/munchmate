import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.presentation.api.v1.authentication import router_auth
from app.infrastructure.database.database import Base, engine
from jose import jwt
from app.infrastructure.security.hashing import SECRET_KEY, ALGORITHM


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
    assert response.json()["message"] == "Login successful"

    assert "access_token" in response.cookies
    token = response.cookies.get("access_token")
    assert token is not None

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "loginuser@example.com"
    assert "exp" in payload


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

