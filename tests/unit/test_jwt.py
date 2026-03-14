from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
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

def test_login_user():
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
    

def test_get_current_user():
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
    assert response.json()["user"] == "test@test.com"