import pytest
from backend.app.presentation.api.routers.users import router
from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.main import app


client = TestClient(app) #simulate the api calls to the router

def test_create_user_success():
    user_payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "securepassword"
    }
    #send a post request to the /users/ endpoint with the user payload
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 200
    data = response.json() #convert the response to json format
    assert data["email"] == user_payload["email"]
    assert data["username"] == user_payload["username"]
    assert "password" not in data #password should not be returned in the response

def test_create_user_email_invalid():
    user_payload = {
        "email": "not_an_email",
        "username": "testuser",
        "password": "securepassword"
    }
    response = client.post("/users/", json=user_payload)
    
    #validation error for email, username, and password
    assert response.status_code == 422 #422 is for unprocessable entity --> data validation fails

def test_creat_user_short_password():
    user_payload = {
        "email": "testuser@example.com",
        "username": "testuser",
        "password": "123"
    }
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 422 
    
def test_creat_user_duplicate_email():
    user_payload = {
        "email": "duplicate@example.com",
        "username": "testuser",
        "password": "123456"
    }
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 200 #this is successfull
    
    #duplicate response
    response = client.post("/users/", json=user_payload)
    assert response.status_code == 400 #bad request --> smth went wrong with the request the client sent (invalid input)