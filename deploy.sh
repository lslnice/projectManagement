#!/bin/bash
set -e

# ============ 配置区（修改这里） ============
GH_USER="lslnice"
# ==========================================

APP_DIR="/www/wwwroot/projectManagement"
MIRROR="ghcr.nju.edu.cn"
COMPOSE_URL="https://raw.githubusercontent.com/$GH_USER/projectmanagement/main/docker-compose.prod.yml"

echo "========== 项目管理系统 一键部署 =========="

# 1. 检查并安装 Docker
if ! command -v docker &> /dev/null; then
    echo "[1/5] Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
    echo "Docker 安装完成"
else
    echo "[1/5] Docker 已安装，跳过"
fi

# 2. 创建部署目录并下载 compose 文件
echo "[2/5] 准备部署文件..."
mkdir -p "$APP_DIR/data"
curl -fsSL "$COMPOSE_URL" -o "$APP_DIR/docker-compose.yml"

# 3. 通过国内镜像拉取（ghcr.nju.edu.cn 代理 ghcr.io）
echo "[3/5] 拉取镜像（通过南大镜像加速）..."
docker pull $MIRROR/$GH_USER/projectmanagement-backend:latest
docker pull $MIRROR/$GH_USER/projectmanagement-frontend:latest

# 4. retag 为 ghcr.io 地址（与 docker-compose.yml 一致）
echo "[4/5] 处理镜像标签..."
docker tag $MIRROR/$GH_USER/projectmanagement-backend:latest  ghcr.io/$GH_USER/projectmanagement-backend:latest
docker tag $MIRROR/$GH_USER/projectmanagement-frontend:latest ghcr.io/$GH_USER/projectmanagement-frontend:latest

# 5. 启动服务
echo "[5/5] 启动服务..."
cd "$APP_DIR"
docker compose up -d

echo ""
echo "========== 部署完成 =========="
echo "访问地址: http://$(hostname -I | awk '{print $1}')"
echo "默认账号: admin"
echo "默认密码: admin123"
echo ""
echo "常用命令:"
echo "  查看状态: cd $APP_DIR && docker compose ps"
echo "  查看日志: cd $APP_DIR && docker compose logs -f"
echo "  更新部署: cd $APP_DIR && docker compose pull && docker compose up -d"
echo "  停止服务: cd $APP_DIR && docker compose down"
