from app.infrastructure.database.user_database import fake_user_db
import pytest


@pytest.fixture(autouse=True)
def clear_db(setup_database): 
    fake_user_db.clear()
    yield
    fake_user_db.clear()

def test_register_user_with_role(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "manager@test.com",
            "username": "manager1",
            "password": "password123",
            "role": "manager"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "manager"
    assert data["message"] == "user registered successfully"

def test_register_user_default_role(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "user@test.com",
            "username": "user001",   
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "user"

def test_login_and_access_me(client):
    client.post(
        "/auth/register",
        json={
            "email": "user@test.com",
            "username": "user001",
            "password": "password123"
        }
    )
    response = client.post(
        "/auth/login",
        json={"email": "user@test.com", "password": "password123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "user@test.com"

def test_manager_dashboard_access(client):
    client.post(
        "/auth/register",
        json={
            "email": "manager@test.com",
            "username": "manager1",
            "password": "password123",
            "role": "manager"
        }
    )
    response = client.post(
        "/auth/login",
        json={"email": "manager@test.com", "password": "password123"}
    )
    token = response.json()["access_token"]

    response = client.get(
        "/auth/manager/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Welcome manager1" in response.json()["message"]

def test_manager_dashboard_forbidden_for_user(client):
    client.post(
        "/auth/register",
        json={
            "email": "user@test.com",
            "username": "user001",
            "password": "password123"
        }
    )
    response = client.post(
        "/auth/login",
        json={"email": "user@test.com", "password": "password123"}
    )
    token = response.json()["access_token"]

    response = client.get(
        "/auth/manager/dashboard",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Manager access required" in response.json()["detail"]