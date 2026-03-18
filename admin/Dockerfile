# frontend/Dockerfile

# 构建阶段
FROM node:18-alpine as build-stage
WORKDIR /app
ENV NODE_OPTIONS=--max-old-space-size=4096
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build  

# 生产环境阶段
FROM nginx:alpine as production-stage
# 复制自定义 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf
# 从构建阶段复制打包好的 dist 文件夹到 Nginx 目录
COPY --from=build-stage /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
