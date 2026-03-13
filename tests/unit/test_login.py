import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.database.user_database import fake_user_db


client = TestClient(app)

# Runs before each test --> keeps DB clean
@pytest.fixture(autouse=True)
def clear_db():
    fake_user_db.clear()
    yield
    fake_user_db.clear()
    
def test_login_success():
    #register first
    client.post("/register", json={
        "username": "keyon123",
        "email": "keyon@example.com",
        "password": "securepass"
    })
    
    response = client.post("/login", json={
    "email": "keyon@example.com",
    "password": "securepass"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_missing_email():
    response = client.post("/login", json={
        "password": "securepass"
    })
    assert response.status_code == 422