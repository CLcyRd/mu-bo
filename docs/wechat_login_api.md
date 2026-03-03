# 微信一键登录 API 文档

## 1. 概述
本接口用于处理微信小程序端的一键登录请求。通过微信提供的 code 和 phone_code，后端完成用户身份校验、手机号获取、用户自动注册/登录，并颁发 JWT 访问令牌。

## 2. 接口定义

### 2.1 微信登录
- **URL**: `/api/auth/wechat/login`
- **Method**: `POST`
- **Content-Type**: `application/json`

### 2.2 请求参数

| 参数名 | 类型 | 必填 | 说明 |
| :--- | :--- | :--- | :--- |
| `code` | string | 是 | `uni.login` 获取的登录凭证 (js_code) |
| `phone_code` | string | 是 | `getPhoneNumber` 回调获取的动态令牌 |

**请求示例**:
```json
{
  "code": "091xxxxxx",
  "phone_code": "142xxxxxx"
}
```

### 2.3 响应参数

| 参数名 | 类型 | 说明 |
| :--- | :--- | :--- |
| `access_token` | string | JWT 访问令牌，用于后续接口鉴权 |
| `token_type` | string | 令牌类型，固定为 "bearer" |

**成功响应示例**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR...",
  "token_type": "bearer"
}
```

**失败响应示例**:
```json
{
  "detail": "WeChat phone verification failed: Invalid code"
}
```

## 3. 错误码说明

| HTTP 状态码 | 错误描述 | 可能原因 |
| :--- | :--- | :--- |
| 400 | Bad Request | 微信 API 调用失败（如 code 过期）、用户状态异常 |
| 500 | Internal Server Error | 数据库操作失败、服务器内部错误 |

## 4. 流程说明
1. **获取手机号**: 后端使用 `phone_code` 调用微信 `getuserphonenumber` 接口获取用户手机号。
2. **获取 OpenID**: 后端使用 `code` 调用微信 `jscode2session` 接口获取 OpenID 和 SessionKey。
3. **用户查找/注册**: 
   - 根据手机号查找数据库中是否存在对应用户。
   - 若不存在，则自动创建新用户，用户名为 `wx_{手机号}`。
   - 若存在，更新用户的 OpenID（如果为空）。
4. **生成 Token**: 为用户生成 JWT Token 并返回。

## 5. 安全与注意事项
- **HTTPS**: 生产环境必须使用 HTTPS。
- **Token 存储**: 前端应将 token 存储在 `Storage` 中，并在后续请求头 `Authorization` 中携带。
- **AppID/Secret**: 后端需配置正确的微信小程序 AppID 和 AppSecret。
