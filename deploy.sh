#!/bin/bash
# ========================================
# 项目管理系统 - 一键部署脚本
# ========================================
# ============ 配置区（修改这里） ============


# ==========================================
# 配置区（请修改为你的信息）
GH_TOKEN="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"
GH_USER="lslnice"
REPO="projectmanagement"
DEPLOY_DIR="/www/wwwroot/projectManagement"

# ========================================
set -e

echo "=== 项目管理系统部署脚本 ==="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "正在安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

# 检查 Docker Compose
if ! docker compose version &> /dev/null; then
    echo "请安装 Docker Compose V2"
    exit 1
fi

# 创建部署目录
mkdir -p ${DEPLOY_DIR}/data

# 登录 ghcr.io
echo ${GH_TOKEN} | docker login ghcr.io -u ${GH_USER} --password-stdin

# 下载 compose 文件
cd ${DEPLOY_DIR}
if [ ! -f "docker-compose.yml" ]; then
    echo "请将 docker-compose.prod.yml 复制到 ${DEPLOY_DIR}/docker-compose.yml"
    exit 1
fi

# 拉取最新镜像
docker compose pull

# 启动服务
docker compose up -d

echo "=== 部署完成 ==="
echo "访问地址: http://$(hostname -I | awk '{print $1}')"
echo "默认账号: admin / admin123"
