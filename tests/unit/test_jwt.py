import pytest
from app.infrastructure.database.user_database import fake_user_db

@pytest.fixture(autouse=True)
def clear_fake_db():
    fake_user_db.clear()
    yield
    fake_user_db.clear()

def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "email": "test@test.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "user registered successfully"

def test_login_user(client):
   
    client.post(
        "/auth/register",
        json={
            "email": "test@test.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    response = client.post(
        "/auth/login",
        json={
            "email": "test@test.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    

def test_get_current_user(client):
   
    client.post(
        "/auth/register",
        json={
            "email": "test@test.com",
            "username": "testuser",
            "password": "password123"
        }
    )
    
    login_response = client.post(
        "/auth/login",
        json={
            "email": "test@test.com",
            "password": "password123"
        }
    )
    
    token = login_response.json()["access_token"]
    
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "test@test.com"