import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import models, database
from app.wechat import wechat_client

client = TestClient(app)

def test_wechat_login_mock():
    old_app_id = wechat_client.app_id
    old_app_secret = wechat_client.app_secret
    wechat_client.app_id = "wx_your_app_id"
    wechat_client.app_secret = "wx_your_app_secret"
    # Use mock codes defined in app/wechat.py
    try:
        response = client.post(
            "/api/auth/wechat/login",
            json={
                "code": "mock_login_code",
                "phone_code": "mock_phone_code"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        db = database.SessionLocal()
        user = db.query(models.User).filter(models.User.phone_number == "13800138000").first()
        assert user is not None
        assert user.openid == "mock_openid_123456"
        assert user.username.startswith("wx_13800138000")
        db.close()
    finally:
        wechat_client.app_id = old_app_id
        wechat_client.app_secret = old_app_secret

def test_wechat_login_fail():
    old_app_id = wechat_client.app_id
    old_app_secret = wechat_client.app_secret
    wechat_client.app_id = "wx_your_app_id"
    wechat_client.app_secret = "wx_your_app_secret"
    # Invalid code
    try:
        response = client.post(
            "/api/auth/wechat/login",
            json={
                "code": "invalid_code",
                "phone_code": "invalid_code"
            }
        )
        assert response.status_code == 400
    finally:
        wechat_client.app_id = old_app_id
        wechat_client.app_secret = old_app_secret

if __name__ == "__main__":
    try:
        print("Testing WeChat Login Mock...")
        test_wechat_login_mock()
        print("PASS")

        print("Testing WeChat Login Fail...")
        test_wechat_login_fail()
        print("PASS")
        
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
