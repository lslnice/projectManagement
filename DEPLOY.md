# 项目管理系统 - 部署说明

## 架构

- **前端**：Vue3 + Element Plus → Nginx (端口 80)
- **后端**：FastAPI → Uvicorn (端口 8000)
- **数据库**：SQLite (文件存储)

## 本地开发

### 启动后端
```bash
cd backend
pip install -r requirements.txt
python run.py
```

### 启动前端
```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000，默认账号 `admin` / `admin123`

## Docker 部署

### 本地构建
```bash
docker compose up -d --build
```

### 生产部署

1. 推送代码到 GitHub main 分支，自动构建镜像
2. 修改 `deploy.sh` 中的 `GH_TOKEN` 和 `GH_USER`
3. 在服务器执行：
```bash
chmod +x deploy.sh && ./deploy.sh
```

## 常用运维

```bash
# 查看日志
docker compose logs -f backend
docker compose logs -f frontend

# 重启
docker compose restart

# 更新
docker compose pull && docker compose up -d

# 数据备份
cp /www/wwwroot/projectManagement/data/project_management.db ./backup_$(date +%Y%m%d).db

# 数据恢复
cp backup.db /www/wwwroot/projectManagement/data/project_management.db
docker compose restart backend
```
