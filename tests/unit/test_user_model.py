import pytest
from app.infrastructure.database.models import Customer
from conftest import TestingSessionLocal

@pytest.fixture(autouse=True)
def clean_customers(setup_database):  
    db = TestingSessionLocal()
    db.query(Customer).delete()
    db.commit()
    db.close()
    yield
    db = TestingSessionLocal()
    db.query(Customer).delete()
    db.commit()
    db.close()

def test_create_user_success(client):
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

def test_create_user_email_invalid(client):
    user_payload = {
        "email": "not_an_email",
        "username": "testuser",
        "password": "securepassword"
    }
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 422

def test_create_user_short_password(client):
    user_payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "123"
    }
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 422

def test_create_user_duplicate_email(client):
    user_payload = {
        "email": "duplicate@example.com",
        "username": "testuser",
        "password": "123456"
    }
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 200

    response = client.post("/users/", json=user_payload)
    assert response.status_code == 400