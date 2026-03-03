import httpx
import logging
import os
from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Load credentials from environment variables, fallback to placeholders/mock for dev
WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "wx_your_app_id")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "wx_your_app_secret")

class WeChatClient:
    def __init__(self, app_id=WECHAT_APP_ID, app_secret=WECHAT_APP_SECRET):
        self.app_id = app_id
        self.app_secret = app_secret

    async def get_access_token(self):
        # MOCK for testing without real credentials
        if self.app_id == "wx_your_app_id":
            logger.warning("Using MOCK WeChat credentials")
            return "mock_access_token"

        url = "https://api.weixin.qq.com/cgi-bin/token"
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat get_access_token error: {data}")
                raise HTTPException(status_code=400, detail=f"WeChat Error: {data.get('errmsg')}")
            return data["access_token"]

    async def get_phone_number(self, code: str):
        # MOCK for testing
        if self.app_id == "wx_your_app_id":
            if code == "mock_phone_code":
                return {
                    "phoneNumber": "13800138000",
                    "purePhoneNumber": "13800138000",
                    "countryCode": "86",
                    "watermark": {"timestamp": 1610000000, "appid": self.app_id}
                }
            else:
                 raise HTTPException(status_code=400, detail="WeChat Error: Invalid code (Mock)")

        access_token = await self.get_access_token()
        url = f"https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}"
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json={"code": code})
            data = response.json()
            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat get_phone_number error: {data}")
                raise HTTPException(status_code=400, detail=f"WeChat Error: {data.get('errmsg')}")
            return data["phone_info"]

    async def code_2_session(self, code: str):
        # MOCK for testing
        if self.app_id == "wx_your_app_id":
            if code == "mock_login_code":
                return {
                    "openid": "mock_openid_123456",
                    "session_key": "mock_session_key",
                    "unionid": "mock_unionid"
                }
            else:
                 raise HTTPException(status_code=400, detail="WeChat Error: Invalid code (Mock)")

        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            data = response.json()
            if "errcode" in data and data["errcode"] != 0:
                logger.error(f"WeChat code_2_session error: {data}")
                raise HTTPException(status_code=400, detail=f"WeChat Error: {data.get('errmsg')}")
            return data

wechat_client = WeChatClient()
