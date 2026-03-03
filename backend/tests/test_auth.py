
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import auth, schemas

client = TestClient(app)

def test_login_admin():
    response = client.post(
        "/api/token",
        data={"username": "admin", "password": "admin"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_login_user():
    response = client.post(
        "/api/token",
        data={"username": "user", "password": "user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    return data["access_token"]

def test_unauthenticated_access():
    response = client.get("/api/bookings/")
    assert response.status_code == 401

def test_unauthorized_access():
    token = test_login_user()
    response = client.get(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_authorized_access():
    token = test_login_admin()
    response = client.get(
        "/api/bookings/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

if __name__ == "__main__":
    # Manually run tests if pytest not installed
    try:
        print("Testing Unauthenticated Access...")
        test_unauthenticated_access()
        print("PASS")

        print("Testing Unauthorized Access (User)...")
        test_unauthorized_access()
        print("PASS")

        print("Testing Authorized Access (Admin)...")
        test_authorized_access()
        print("PASS")
        
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
