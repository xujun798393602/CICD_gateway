#!/bin/bash
# ==============================================================================
# 代码质量门禁系统 - 查看日志脚本
# ==============================================================================

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_DIR/deploy"

cd "$DEPLOY_DIR"

# 设置Docker Compose命令
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# 查看日志
if [ -n "$1" ]; then
    $COMPOSE_CMD logs -f "$1"
else
    $COMPOSE_CMD logs -f
fi
