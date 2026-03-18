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
ALLOW_ORIGINS=https://shxiejinf.cn,https://www.shxiejinf.cn,https://api.shxiejinf.cn
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
# VITE_API_URL=https://api.shxiejinf.cn
npm run build
```

构建完成后会生成 `dist` 目录。

### 3.2 上传文件

将 `dist` 目录下的所有文件上传到服务器，例如 `/var/www/museum_booking/admin_dist`。

## 4. Nginx 配置 (核心步骤)

推荐使用 Docker 启动后端和管理端容器，再由宿主机 Nginx 做 HTTPS 入口转发。

先在项目根目录启动容器：

```bash
docker compose up -d --build
```

当前端口映射为：

- `127.0.0.1:8080` -> 管理端容器
- `127.0.0.1:8000` -> 后端容器

编辑 `/etc/nginx/sites-available/museum`：

```nginx
server {
    listen 80;
    server_name shxiejinf.cn www.shxiejinf.cn api.shxiejinf.cn;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name shxiejinf.cn www.shxiejinf.cn;

    ssl_certificate /etc/letsencrypt/live/shxiejinf.cn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/shxiejinf.cn/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl http2;
    server_name api.shxiejinf.cn;

    ssl_certificate /etc/letsencrypt/live/shxiejinf.cn/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/shxiejinf.cn/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
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

也可直接使用仓库模板文件 [nginx.shxiejinf.cn.conf](file:///g:/museum_booking/mu-bo/docs/nginx.shxiejinf.cn.conf)。

## 5. 微信小程序发布

### 5.1 修改服务器地址

1.  打开 `miniprogram` 项目。
2.  找到 API 请求的基础路径配置（通常在 `utils/request.js` 或 `main.js` 中）。
3.  将 `http://localhost:8000` 修改为线上 HTTPS 地址：`https://api.shxiejinf.cn`。

### 5.2 微信后台配置

1.  登录 [微信公众平台](https://mp.weixin.qq.com/)。
2.  进入 **开发 -> 开发管理 -> 开发设置**。
3.  在 **服务器域名** 中配置 `request合法域名`，填入 `https://api.shxiejinf.cn`。

### 5.3 上传与审核

1.  在微信开发者工具中点击 **上传**。
2.  填写版本号和备注。
3.  登录微信公众平台，在 **版本管理** 中将上传的体验版提交审核。
4.  审核通过后即可发布上线。

## 6. HTTPS 配置 (推荐)

使用 Certbot 自动配置 SSL：

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d shxiejinf.cn -d www.shxiejinf.cn -d api.shxiejinf.cn
```

按照提示操作即可开启 HTTPS。
