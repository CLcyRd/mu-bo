# 博物馆预约系统云端部署指南

本文档详细介绍了如何将博物馆预约系统（后端、管理后台、小程序）部署到云服务器（以 Ubuntu 为例）。

## 1. 准备工作

*   **云服务器**: 推荐 Ubuntu 20.04/22.04 LTS。
*   **域名**: 已备案域名（微信小程序强制要求 HTTPS 和备案域名）。
*   **SSL 证书**: 用于 HTTPS（可使用 Let's Encrypt 免费证书）。
*   **软件环境**:
    *   Nginx (Web 服务器/反向代理)
    *   Python 3.9+ (后端)
    *   Node.js (用于构建前端，也可在本地构建后上传)
    *   PostgreSQL (生产环境数据库，可选 SQLite)

## 2. 后端部署 (FastAPI)

### 2.1 环境配置

登录服务器并安装 Python 和 venv：

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx git
```

### 2.2 代码部署

1.  克隆代码到服务器（例如 `/var/www/museum_booking`）。
2.  进入后端目录并创建虚拟环境：

```bash
cd /var/www/museum_booking/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # 生产环境推荐使用 Gunicorn
```

### 2.3 配置环境变量

创建 `.env` 文件（生产环境配置）：

```env
DATABASE_URL=sqlite:///./museum.db  # 或 postgresql://user:pass@localhost/db
ALLOW_ORIGINS=https://your-admin-domain.com
```

### 2.4 使用 Systemd 管理进程

创建服务文件 `/etc/systemd/system/museum_backend.service`:

```ini
[Unit]
Description=Gunicorn instance to serve Museum Booking API
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/museum_booking/backend
Environment="PATH=/var/www/museum_booking/backend/venv/bin"
ExecStart=/var/www/museum_booking/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 127.0.0.1:8000 app.main:app

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl start museum_backend
sudo systemctl enable museum_backend
```

## 3. 管理后台部署 (Vue 3)

### 3.1 构建项目

**在本地开发机执行**（或服务器安装 Node.js 后执行）：

```bash
cd admin
# 修改 .env.production 中的 API 地址为线上地址
# VITE_API_URL=https://api.your-domain.com
npm run build
```

构建完成后会生成 `dist` 目录。

### 3.2 上传文件

将 `dist` 目录下的所有文件上传到服务器，例如 `/var/www/museum_booking/admin_dist`。

## 4. Nginx 配置 (核心步骤)

配置 Nginx 以同时服务前端静态文件和反向代理后端 API。

编辑 `/etc/nginx/sites-available/museum`：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    # 强制跳转 HTTPS (建议配置 SSL 后开启)
    # return 301 https://$host$request_uri;
    
    # 管理后台前端
    location / {
        root /var/www/museum_booking/admin_dist;
        index index.html;
        try_files $uri $uri/ /index.html;  # 解决 Vue Router History 模式刷新 404
    }

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;  # 转发给 Gunicorn
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置并重启 Nginx：

```bash
sudo ln -s /etc/nginx/sites-available/museum /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 5. 微信小程序发布

### 5.1 修改服务器地址

1.  打开 `miniprogram` 项目。
2.  找到 API 请求的基础路径配置（通常在 `utils/request.js` 或 `main.js` 中）。
3.  将 `http://localhost:8000` 修改为线上 HTTPS 地址：`https://your-domain.com`。

### 5.2 微信后台配置

1.  登录 [微信公众平台](https://mp.weixin.qq.com/)。
2.  进入 **开发 -> 开发管理 -> 开发设置**。
3.  在 **服务器域名** 中配置 `request合法域名`，填入 `https://your-domain.com`。

### 5.3 上传与审核

1.  在微信开发者工具中点击 **上传**。
2.  填写版本号和备注。
3.  登录微信公众平台，在 **版本管理** 中将上传的体验版提交审核。
4.  审核通过后即可发布上线。

## 6. HTTPS 配置 (推荐)

使用 Certbot 自动配置 SSL：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

按照提示操作即可开启 HTTPS。
