#!/bin/bash
# ==============================================================================
# 代码质量门禁系统 - 查看状态脚本
# ==============================================================================

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

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

echo "============================== 服务状态 =============================="
$COMPOSE_CMD ps
echo ""

echo "============================== 健康检查 =============================="
# 检查应用健康状态
HEALTH=$(curl -sf http://localhost:8000/api/v1/health 2>/dev/null)
if [ $? -eq 0 ]; then
    echo -e "应用服务: ${GREEN}正常${NC}"
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
else
    echo -e "应用服务: ${RED}异常${NC}"
fi
echo ""

echo "============================== 资源使用 =============================="
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" $(docker ps -q --filter name=quality-gate) 2>/dev/null || echo "无法获取资源使用信息"
