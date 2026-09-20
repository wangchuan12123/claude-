#!/bin/bash
# ============================================================
# 鸾鸟 (LuaN1aoAgent) 启动脚本
# 启动 Web 控制台 + 知识服务
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LUAN1AO_DIR="$HOME/LuaN1aoAgent"

echo "=========================================="
echo "  鸾鸟 LuaN1aoAgent — 服务启动"
echo "=========================================="

# Check if LuaN1aoAgent exists
if [ ! -d "$LUAN1AO_DIR" ]; then
    echo "[ERROR] LuaN1aoAgent not found at $LUAN1AO_DIR"
    echo "  Clone: git clone https://github.com/SanMuzZzZz/LuaN1aoAgent.git ~/LuaN1aoAgent"
    exit 1
fi

cd "$LUAN1AO_DIR"

# Activate venv
if [ -f venv/Scripts/activate ]; then
    source venv/Scripts/activate
elif [ -f venv/bin/activate ]; then
    source venv/bin/activate
else
    echo "[ERROR] Python venv not found. Run: python -m venv venv && source venv/Scripts/activate && pip install -r requirements.txt"
    exit 1
fi

# Verify API key
if [ -z "$LLM_API_KEY" ]; then
    # Load from .env
    export $(grep -v '^#' .env | xargs 2>/dev/null || true)
fi

if [ -z "$LLM_API_KEY" ]; then
    echo "[ERROR] LLM_API_KEY not set. Please configure .env"
    exit 1
fi

echo "[OK] API Key: ${LLM_API_KEY:0:20}..."
echo "[OK] Model: $LLM_DEFAULT_MODEL"
echo ""

# Function: Start Knowledge Service
start_knowledge_service() {
    echo "[INFO] Starting Knowledge Service on :${KNOWLEDGE_SERVICE_PORT:-8081}..."
    python -m rag.knowledge_service &
    KNOWLEDGE_PID=$!
    echo "       PID: $KNOWLEDGE_PID"
    sleep 2
}

# Function: Start Web Console
start_web() {
    echo "[INFO] Starting Web Console on :${WEB_PORT:-8000}..."
    echo "       Open http://127.0.0.1:${WEB_PORT:-8000} in browser"
    echo ""
    python -m web.server &
    WEB_PID=$!
    echo "       PID: $WEB_PID"
}

# Main
start_knowledge_service
start_web

echo ""
echo "=========================================="
echo "  鸾鸟已启动"
echo "  Web UI:  http://127.0.0.1:${WEB_PORT:-8000}"
echo "  Knowledge: http://127.0.0.1:${KNOWLEDGE_SERVICE_PORT:-8081}"
echo ""
echo "  Claude 集成:"
echo "    python ~/.claude/tools/luan1ao_client.py launch '<goal>'"
echo ""
echo "  Press Ctrl+C to stop all services"
echo "=========================================="

# Trap cleanup
cleanup() {
    echo ""
    echo "[INFO] Stopping services..."
    [ -n "$WEB_PID" ] && kill "$WEB_PID" 2>/dev/null
    [ -n "$KNOWLEDGE_PID" ] && kill "$KNOWLEDGE_PID" 2>/dev/null
    echo "[INFO] Done."
}
trap cleanup EXIT INT TERM

# Wait
wait
