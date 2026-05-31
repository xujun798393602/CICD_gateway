#!/bin/bash
# ==============================================================================
# 代码质量门禁系统 - 数据备份脚本
# ==============================================================================

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$PROJECT_DIR/deploy"

# 加载环境变量
source "$DEPLOY_DIR/.env"

# 备份目录
BACKUP_DIR="$PROJECT_DIR/backups"
mkdir -p "$BACKUP_DIR"

# 备份文件名
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/quality_gate_backup_$TIMESTAMP.sql"

# 设置Docker Compose命令
cd "$DEPLOY_DIR"
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# 执行备份
print_info "开始备份数据库..."
$COMPOSE_CMD exec -T mysql mysqldump \
    -u root \
    -p"${MYSQL_ROOT_PASSWORD}" \
    --single-transaction \
    --routines \
    --triggers \
    quality_gate > "$BACKUP_FILE"

# 压缩备份文件
gzip "$BACKUP_FILE"

print_success "备份完成: ${BACKUP_FILE}.gz"

# 清理30天前的备份
print_info "清理旧备份..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete 2>/dev/null || true

print_success "备份任务完成"
