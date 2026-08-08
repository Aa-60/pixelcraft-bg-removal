#!/bin/bash
# PixelCraft 一键部署脚本 - Oracle Cloud ARM
# 在 Oracle Cloud 实例 SSH 终端中运行: bash setup_oracle.sh

set -e

echo "=========================================="
echo "  PixelCraft AI 抠图 - 一键部署"
echo "  模型: BiRefNet | Oracle Cloud ARM"
echo "=========================================="

# 1. 安装 Docker
echo "[1/6] 安装 Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    sudo systemctl enable docker
    sudo systemctl start docker
    sudo usermod -aG docker $USER
    echo "  Docker 安装完成"
else
    echo "  Docker 已安装"
fi

# 2. 安装 Git
echo "[2/6] 安装 Git..."
if ! command -v git &> /dev/null; then
    sudo dnf install -y git
else
    echo "  Git 已安装"
fi

# 3. 克隆项目
echo "[3/6] 克隆项目..."
cd /home/$USER
if [ -d "pixelcraft-bg-removal" ]; then
    cd pixelcraft-bg-removal
    git pull origin main || true
else
    git clone https://github.com/Aa-60/pixelcraft-bg-removal.git
    cd pixelcraft-bg-removal
fi

# 4. 构建Docker镜像
echo "[4/6] 构建 Docker 镜像（需要3-5分钟）..."
sudo docker build -t pixelcraft .

# 5. 停止旧容器（如果有）
echo "[5/6] 启动容器..."
sudo docker rm -f pixelcraft 2>/dev/null || true

# 启动新容器，端口7860
sudo docker run -d \
    --name pixelcraft \
    --restart always \
    -p 7860:7860 \
    -e PORT=7860 \
    --memory=4g \
    pixelcraft

# 6. 等待启动
echo "[6/6] 等待服务启动..."
sleep 5

# 获取公网IP
PUBLIC_IP=$(curl -s http://169.254.169.254/opc/v2/instance/ | python3 -c "import sys,json; print(json.load(sys.stdin).get('publicIpAddress','unknown'))" 2>/dev/null || echo "unknown")

echo ""
echo "=========================================="
echo "  部署完成!"
echo "=========================================="
echo ""
echo "  访问地址: http://$PUBLIC_IP:7860"
echo ""
echo "  注意: BiRefNet 模型首次加载需要1-2分钟"
echo "  首次访问抠图功能时会下载模型(约170MB)"
echo ""
echo "  查看日志: sudo docker logs -f pixelcraft"
echo "  重启服务: sudo docker restart pixelcraft"
echo "=========================================="
