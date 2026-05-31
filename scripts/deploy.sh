#!/bin/bash
# ==============================================================================
# 代码质量门禁系统 - 一键部署脚本
# ==============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_DIR/deploy"

# 进入部署目录
cd "$DEPLOY_DIR"

# ==================== 前置检查 ====================
print_info "执行前置检查..."

# 检查Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker未安装，请先安装Docker"
    print_info "安装命令: curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose未安装，请先安装"
    print_info "安装命令: sudo apt install docker-compose-plugin"
    exit 1
fi

# 设置Docker Compose命令
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

print_success "Docker和Docker Compose已安装"

# ==================== 环境配置 ====================
print_info "检查环境配置..."

# 检查.env文件
if [ ! -f .env ]; then
    print_warning ".env文件不存在，从模板创建..."
    cp .env.example .env
    print_warning "请编辑 .env 文件配置数据库密码等参数"
    print_warning "配置完成后重新运行此脚本"
    exit 0
fi

# 加载环境变量
source .env

# ==================== 创建目录 ====================
print_info "创建必要目录..."

mkdir -p "$DEPLOY_DIR/nginx/ssl"
mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/reports"
mkdir -p "$PROJECT_DIR/config"

# ==================== 停止旧容器 ====================
print_info "停止旧容器（如果存在）..."

$COMPOSE_CMD down --remove-orphans 2>/dev/null || true

# ==================== 构建镜像 ====================
print_info "构建应用镜像..."

$COMPOSE_CMD build --no-cache app

# ==================== 启动服务 ====================
print_info "启动所有服务..."

$COMPOSE_CMD up -d

# ==================== 等待服务就绪 ====================
print_info "等待服务启动..."

# 等待MySQL就绪
print_info "等待MySQL就绪..."
for i in {1..60}; do
    if $COMPOSE_CMD exec -T mysql mysqladmin ping -h localhost -u root -p"${MYSQL_ROOT_PASSWORD}" --silent 2>/dev/null; then
        print_success "MySQL已就绪"
        break
    fi
    if [ $i -eq 60 ]; then
        print_error "MySQL启动超时"
        $COMPOSE_CMD logs mysql
        exit 1
    fi
    sleep 2
done

# 等待Redis就绪
print_info "等待Redis就绪..."
for i in {1..30}; do
    if $COMPOSE_CMD exec -T redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        print_success "Redis已就绪"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Redis启动超时"
        $COMPOSE_CMD logs redis
        exit 1
    fi
    sleep 1
done

# 等待应用就绪
print_info "等待应用服务就绪..."
for i in {1..60}; do
    if curl -sf http://localhost:${APP_PORT:-8000}/api/v1/health > /dev/null 2>&1; then
        print_success "应用服务已就绪"
        break
    fi
    if [ $i -eq 60 ]; then
        print_error "应用服务启动超时"
        $COMPOSE_CMD logs app
        exit 1
    fi
    sleep 2
done

# ==================== 验证部署 ====================
print_info "验证部署状态..."

echo ""
echo "============================== 服务状态 =============================="
$COMPOSE_CMD ps
echo ""

# 健康检查
echo "============================== 健康检查 =============================="
HEALTH_RESPONSE=$(curl -s http://localhost:${APP_PORT:-8000}/api/v1/health)
echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
echo ""

# API测试
echo "============================== API测试 =============================="
print_info "测试触发扫描接口..."
TRIGGER_RESPONSE=$(curl -s -X POST http://localhost:${APP_PORT:-8000}/api/v1/scans/trigger \
    -H "Content-Type: application/json" \
    -d '{
        "project_id": "deploy_test",
        "repository_url": "https://example.com/test/repo",
        "branch": "main",
        "commit_sha": "test123",
        "trigger_type": "manual"
    }')
echo "$TRIGGER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TRIGGER_RESPONSE"
echo ""

# ==================== 部署完成 ====================
echo "======================================================================"
print_success "部署完成！"
echo "======================================================================"
echo ""
echo "服务访问地址:"
echo "  - API服务:    http://localhost:${APP_PORT:-8000}"
echo "  - API文档:    http://localhost:${APP_PORT:-8000}/docs"
echo "  - 报告页面:   http://localhost:${REPORT_PORT:-8080}"
echo "  - Nginx代理:  http://localhost:${HTTP_PORT:-80}"
echo ""
echo "常用命令:"
echo "  - 查看日志:   $COMPOSE_CMD logs -f [服务名]"
echo "  - 停止服务:   $COMPOSE_CMD down"
echo "  - 重启服务:   $COMPOSE_CMD restart [服务名]"
echo "  - 查看状态:   $COMPOSE_CMD ps"
echo ""
echo "======================================================================"
