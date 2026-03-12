# 咨询发布后端部署说明

## 1. 环境要求

- Python 3.10+
- MySQL 8.0+（推荐生产环境）
- Windows/Linux 均可

## 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 3. 配置项

通过环境变量配置数据库连接与连接池参数：

- `DATABASE_URL`：数据库连接串
  - MySQL 示例：`mysql+pymysql://user:password@127.0.0.1:3306/museum?charset=utf8mb4`
  - 本地默认：`sqlite:///./museum.db`
- `DB_POOL_SIZE`：连接池大小，默认 `10`
- `DB_MAX_OVERFLOW`：额外连接数，默认 `20`
- `DB_POOL_RECYCLE`：连接回收秒数，默认 `1800`
- `DB_POOL_TIMEOUT`：获取连接超时时间，默认 `30`

## 4. 初始化数据库

MySQL 环境执行：

```bash
mysql -u root -p museum < init_consultation.sql
```

应用启动后也会自动创建 ORM 定义表结构（`create_all`），但生产环境建议优先使用 SQL 脚本初始化。

## 5. 启动服务

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 6. 核心接口

- `POST /api/consultations`：创建咨询（草稿/发布）
- `PUT /api/consultations/{id}`：编辑咨询并写入版本历史
- `PATCH /api/consultations/{id}/status`：单条状态切换
- `POST /api/consultations/bulk/status`：批量状态切换
- `GET /api/consultations`：条件筛选 + 分页查询
- `GET /api/consultations/{id}`：查询单篇详情
- `GET /api/consultations/{id}/versions`：查询修改历史

写接口支持请求头 `Idempotency-Key` 实现幂等防重。

## 7. 统一响应格式

所有新咨询接口返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

## 8. 错误码规范

- `0`：成功
- `1000`：通用业务错误（HTTPException）
- `1001`：参数校验失败
- `2001`：正文为空或清洗后无有效内容
- `2002`：幂等键冲突（同键不同请求体）
- `2003`：无权限操作
- `2004`：咨询不存在
- `2005`：更新字段为空
- `2006`：批量操作未命中记录
- `5000`：服务器内部错误
