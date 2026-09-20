#!/bin/bash
# ============================================================
# PentAGI 部署脚本
# 检查 Docker 环境并部署 PentAGI
# ============================================================

set -e

PENTAGI_DIR="$HOME/pentagi"
PENTAGI_REPO="https://github.com/vxcontrol/pentagi.git"

echo "=========================================="
echo "  PentAGI — 部署检查"
echo "=========================================="
echo ""

# Step 1: Check Docker
echo "[1/4] Checking Docker..."
if command -v docker &>/dev/null && docker info &>/dev/null 2>&1; then
    echo "  [OK] Docker is running"
    DOCKER_OK=true
elif command -v docker &>/dev/null; then
    echo "  [WARN] Docker installed but not running. Start Docker Desktop first."
    DOCKER_OK=false
else
    echo "  [MISSING] Docker not found."
    echo ""
    echo "  Options to install:"
    echo "    A) Docker Desktop (GUI, recommended for Windows):"
    echo "       https://docs.docker.com/desktop/setup/install/windows-install/"
    echo ""
    echo "    B) Docker Engine in WSL (CLI, lighter):"
    echo "       wsl --install -d Ubuntu-24.04"
    echo "       wsl -d Ubuntu-24.04"
    echo "       curl -fsSL https://get.docker.com | sudo sh"
    echo "       sudo usermod -aG docker \$USER"
    echo ""
    read -p "  Choose option (A/B/Skip): " DOCKER_CHOICE
    if [ "$DOCKER_CHOICE" = "A" ]; then
        echo "  Please install Docker Desktop from the URL above, then re-run this script."
        exit 0
    elif [ "$DOCKER_CHOICE" = "B" ]; then
        echo "  Installing WSL + Docker Engine..."
        wsl --install -d Ubuntu-24.04
        echo "  After WSL installs, run:"
        echo "    wsl -d Ubuntu-24.04"
        echo "    curl -fsSL https://get.docker.com | sudo sh"
        echo "    sudo usermod -aG docker \$USER"
        echo "  Then re-run this script."
        exit 0
    else
        DOCKER_OK=false
    fi
fi

if [ "$DOCKER_OK" != "true" ]; then
    echo "  [SKIP] Docker not available. Skipping PentAGI deployment."
    echo "  PentAGI requires Docker for sandboxed execution."
    exit 0
fi

# Step 2: Clone repository
echo "[2/4] Cloning PentAGI..."
if [ -d "$PENTAGI_DIR" ]; then
    echo "  [EXISTS] $PENTAGI_DIR — pulling latest..."
    cd "$PENTAGI_DIR" && git pull
else
    git clone "$PENTAGI_REPO" "$PENTAGI_DIR"
    cd "$PENTAGI_DIR"
fi

# Step 3: Configure environment
echo "[3/4] Configuring PentAGI..."
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || true
    echo "  [INFO] Edit $PENTAGI_DIR/.env to configure:"
    echo "    - LLM_API_KEY (use DeepSeek/Claude API key)"
    echo "    - LLM_PROVIDER"
    echo "    - Database credentials"
fi

# Step 4: Launch
echo "[4/4] Starting PentAGI..."
echo ""
echo "  To start PentAGI:"
echo "    cd $PENTAGI_DIR"
echo "    docker compose up -d"
echo ""
echo "  To stop:"
echo "    docker compose down"
echo ""
echo "  Web UI: http://localhost:3000 (default)"
echo "  API:    http://localhost:8080 (default)"
echo ""
echo "=========================================="
echo "  PentAGI deployment complete!"
echo "=========================================="
