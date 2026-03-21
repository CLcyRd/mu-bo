# 博物馆预约系统 (电影艺术家故居主题)

本项目是一个完整的博物馆预约系统，包含后端服务、Web管理后台和微信小程序客户端。

## 目录结构

*   `backend/`: Python FastAPI 后端服务
*   `admin/`: Vue 3 + Element Plus 管理后台
*   `miniprogram/`: Uni-app 微信小程序

## 环境要求

*   Node.js (推荐 v16+)
*   Python (推荐 3.9+)
*   微信开发者工具

## 运行步骤

### 1. 启动后端服务 (Backend)

后端服务运行在 `http://localhost:8000`，使用 SQLite 数据库。

```bash
# 进入后端目录
cd backend

# 创建虚拟环境 (推荐)
python -m venv venv

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate
# 激活虚拟环境 (Mac/Linux)
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload
```

启动成功后，可以访问 [http://localhost:8000/docs](http://localhost:8000/docs) 查看 API 文档。

### 2. 启动管理后台 (Admin)

管理后台运行在 `http://localhost:5173`。

```bash
# 进入管理后台目录
cd admin

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

*   **访问地址**: http://localhost:5173
*   **默认账号**: `admin`
*   **默认密码**: `admin` (如果代码中未硬编码验证，可直接登录)

### 3. 运行微信小程序 (Mini Program)

```bash
# 进入小程序目录
cd miniprogram

# 安装依赖
npm install

# 编译运行 (生成微信小程序代码)
npm run dev:mp-weixin
```

### 4. 部署命令

```bash
# 把新代码拉到服务器上
git pull origin main  # 如果你使用的是 Git
```
```bash
# 重新构建并平滑重启容器（Docker 会自动停止旧容器，启动新容器）：
sudo docker compose up --build -d
```
```bash
# 清理废弃的无用镜像（每次重新构建都会产生一些旧的、不再使用的镜像占用磁盘空间）：
sudo docker image prune -f
```

**导入微信开发者工具**:
1. 打开微信开发者工具。
2. 点击“导入项目”或“打开项目”。
3. 选择目录：`g:\museum_booking\mu-bo\miniprogram\dist\dev\mp-weixin`。
4. AppID 可使用测试号。
5. 确保微信开发者工具中“详情” -> “本地设置” -> 勾选“不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书” (开发环境下需要，因为后端是 localhost)。

## 注意事项

*   **跨域问题**: 后端已配置 CORS 允许 `localhost:5173` 等访问，如遇到跨域错误请检查 `backend/app/main.py` 中的 `allow_origins` 设置。
*   **数据库**: 默认会在 `backend/` 目录下生成 `museum.db` SQLite 文件。如果需要重置数据，只需删除该文件并重启后端服务即可。
