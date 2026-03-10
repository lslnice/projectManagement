#!/bin/bash
set -e

# ============ 配置区（修改这里） ============
GH_TOKEN="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"
GH_USER="lslnice"
# ==========================================

APP_DIR="/www/wwwroot/financialManagement"
COMPOSE_URL="https://raw.githubusercontent.com/$GH_USER/financialManagement/main/docker-compose.prod.yml"

echo "========== 财务管理系统 一键部署 =========="

# 1. 检查并安装 Docker
if ! command -v docker &> /dev/null; then
    echo "[1/5] Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
    echo "Docker 安装完成"
else
    echo "[1/5] Docker 已安装，跳过"
fi

# 2. 登录 GitHub Container Registry
echo "[2/5] 登录镜像仓库..."
echo "$GH_TOKEN" | docker login ghcr.io -u "$GH_USER" --password-stdin

# 3. 创建部署目录并下载 compose 文件
echo "[3/5] 准备部署文件..."
mkdir -p "$APP_DIR/data"
curl -fsSL -H "Authorization: token $GH_TOKEN" "$COMPOSE_URL" -o "$APP_DIR/docker-compose.yml"

# 4. 拉取最新镜像
echo "[4/5] 拉取最新镜像..."
cd "$APP_DIR"
docker compose pull

# 5. 启动服务
echo "[5/5] 启动服务..."
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
