import pytest
from app.infrastructure.database.user_database import fake_user_db
from app.infrastructure.database.models import RevokedToken
from conftest import TestingSessionLocal


@pytest.fixture(autouse=True)
def clear_state():
    fake_user_db.clear()
   
    db = TestingSessionLocal()
    db.query(RevokedToken).delete()
    db.commit()
    db.close()
    yield
    fake_user_db.clear()
    db = TestingSessionLocal()
    db.query(RevokedToken).delete()
    db.commit()
    db.close()

def register_and_login(client):
    client.post("/auth/register", json={
        "email": "user@test.com",
        "username": "user001",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "email": "user@test.com",
        "password": "password123"
    })
    return response.json()["access_token"]


def test_logout_success(client):
    token = register_and_login(client)
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"


def test_revoked_token_cannot_access_me(client):
    token = register_and_login(client)
    client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_logout_without_token(client):
    response = client.post("/auth/logout")
    assert response.status_code == 401


def test_cannot_logout_twice(client):
    token = register_and_login(client)
    client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    response = client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401