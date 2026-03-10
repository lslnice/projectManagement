#!/bin/bash
# ========================================
# 项目管理系统 - 一键部署脚本
# ========================================
# ============ 配置区（修改这里） ============
GH_TOKEN="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"
GH_USER="lslnice"
REPO="projectmanagement"
DEPLOY_DIR="/www/wwwroot/projectManagement"
# ==========================================

set -e

echo "=== 项目管理系统部署脚本 ==="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo ">>> 正在安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
    echo ">>> Docker 安装完成"
fi

# 检查 Docker Compose
if ! docker compose version &> /dev/null; then
    echo "错误：未找到 Docker Compose V2，请升级 Docker 到 20.10+ 版本"
    exit 1
fi

# 创建部署目录
mkdir -p ${DEPLOY_DIR}/data
cd ${DEPLOY_DIR}

# 登录 ghcr.io
echo ">>> 登录 GitHub Container Registry..."
echo ${GH_TOKEN} | docker login ghcr.io -u ${GH_USER} --password-stdin

# 从 GitHub 下载最新的 docker-compose.prod.yml
echo ">>> 下载 docker-compose 配置..."
curl -fsSL \
  -H "Authorization: token ${GH_TOKEN}" \
  "https://raw.githubusercontent.com/${GH_USER}/${REPO}/main/docker-compose.prod.yml" \
  -o docker-compose.yml

echo ">>> 拉取最新镜像..."
docker compose pull

echo ">>> 启动服务..."
docker compose up -d

echo ""
echo "========================================="
echo "  部署完成！"
echo "  访问地址: http://$(hostname -I | awk '{print $1}')"
echo "  默认账号: admin / 密码: admin123"
echo "========================================="
