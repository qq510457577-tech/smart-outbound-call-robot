# 部署指南

## 本地开发

### 前置条件

- Python 3.8+
- 阿里云账号 + OutboundBot 实例
- 有效的 AccessKey ID/Secret

### 步骤

```bash
# 1. 克隆项目
git clone https://github.com/qq510457577-tech/smart-outbound-call-robot.git
cd smart-outbound-call-robot

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的凭据

# 4. 启动服务
python api_server.py

# 5. 访问控制台
# 浏览器打开: frontend/index.html
```

---

## 生产环境部署

### 方案一：Gunicorn + Nginx（推荐）

#### 1. 安装 Gunicorn

```bash
pip install gunicorn
```

#### 2. 启动服务

```bash
gunicorn -w 4 -b 0.0.0.0:5000 api_server:app
```

#### 3. Nginx 反向代理

```nginx
server {
    listen 80;
    server_name outbound-bot.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 静态文件直接由 Nginx 提供
    location /frontend/ {
        alias /path/to/smart-outbound-call-robot/frontend/;
        expires 30d;
    }
}
```

#### 4. Systemd 服务

```ini
# /etc/systemd/system/outbound-bot.service
[Unit]
Description=Smart Outbound Call Robot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/smart-outbound-call-robot
Environment="PATH=/opt/smart-outbound-call-robot/venv/bin"
ExecStart=/opt/smart-outbound-call-robot/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 api_server:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable outbound-bot
sudo systemctl start outbound-bot
sudo systemctl status outbound-bot
```

### 方案二：Docker 部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api_server:app"]
```

```bash
docker build -t outbound-bot .
docker run -d -p 5000:5000 --env-file .env outbound-bot
```

---

## 安全建议

1. **AccessKey 管理**: 建议使用 RAM 子账号，最小权限原则
2. **HTTPS**: 生产环境务必启用 HTTPS
3. **API 鉴权**: 当前 API 无鉴权，建议增加 JWT / API Key 中间件
4. **日志审计**: 开启访问日志和错误日志
5. **并发控制**: 合理设置 `DEFAULT_CONCURRENCY`，避免触发阿里云限流

---

## 常见问题

### Q: 启动时提示 "ModuleNotFoundError: alibabacloud_outboundbot20191226"

```bash
pip install alibabacloud_outboundbot20191226
```

### Q: 阿里云 API 返回认证失败

检查 `.env` 中的 `ACCESS_KEY_ID` 和 `ACCESS_KEY_SECRET` 是否正确，确认 AK 未被禁用。

### Q: 实例列表为空

确认 `OUTBOUNDBOT_INSTANCE_ID` 配置正确，且该实例已开通 Outbound Bot 服务。

### Q: Web 控制台无法连接 API

检查 `api_server.py` 是否正在运行，以及前端页面中配置的 API 地址是否正确。
