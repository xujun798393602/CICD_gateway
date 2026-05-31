# 代码质量门禁系统 - Docker部署指南

## 快速开始

### 1. 环境准备

确保已安装：
- Docker 20.10+
- Docker Compose 2.0+

```bash
# 检查Docker版本
docker --version

# 检查Docker Compose版本
docker-compose --version
# 或
docker compose version
```

### 2. 配置环境变量

```bash
cd deploy

# 从模板创建配置文件
cp .env.example .env

# 编辑配置文件
vi .env
```

主要配置项：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| MYSQL_ROOT_PASSWORD | MySQL root密码 | RootPass123! |
| DB_USER | 数据库用户 | gate_user |
| DB_PASSWORD | 数据库密码 | GatePass123! |
| APP_PORT | API服务端口 | 8000 |
| HTTP_PORT | Nginx HTTP端口 | 80 |
| REPORT_PORT | 报告服务端口 | 8080 |

### 3. 一键部署

```bash
# 方式一：使用部署脚本
./scripts/deploy.sh

# 方式二：手动部署
cd deploy
docker-compose up -d
```

### 4. 验证部署

```bash
# 查看服务状态
docker-compose ps

# 健康检查
curl http://localhost:8000/api/v1/health

# 查看日志
docker-compose logs -f app
```

---

## 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| app | 8000 | FastAPI应用服务 |
| mysql | 3306 | MySQL数据库 |
| redis | 6379 | Redis缓存 |
| nginx | 80 | Nginx反向代理 |
| report-server | 8080 | 报告Web服务 |

---

## 常用命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart [服务名]

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [服务名]
```

### 数据备份

```bash
# 备份数据库
./scripts/backup.sh

# 手动备份
docker-compose exec mysql mysqldump -u root -p quality_gate > backup.sql
```

### 数据恢复

```bash
# 恢复数据库
docker-compose exec -T mysql mysql -u root -p quality_gate < backup.sql
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并部署
docker-compose build --no-cache app
docker-compose up -d
```

---

## 目录结构

```
deploy/
├── docker-compose.yml      # Docker Compose配置
├── Dockerfile              # 应用镜像构建文件
├── .env.example            # 环境变量模板
├── .env                    # 环境变量配置（需创建）
├── README.md               # 本文件
├── mysql/
│   ├── init.sql            # 数据库初始化脚本
│   └── my.cnf              # MySQL配置文件
└── nginx/
    ├── nginx.conf          # Nginx主配置
    ├── conf.d/
    │   └── default.conf    # 站点配置
    ├── report-server.conf  # 报告服务配置
    └── ssl/                # SSL证书目录
```

---

## API接口

部署完成后可访问：

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/v1/health | GET | 健康检查 |
| /api/v1/scans/trigger | POST | 触发扫描 |
| /api/v1/scans/{scan_id}/status | GET | 查询扫描状态 |
| /api/v1/scans/{scan_id}/results | POST | 上报扫描结果 |
| /api/v1/reports/generate | POST | 生成报告 |
| /api/v1/reports/{report_id} | GET | 查询报告 |
| /api/v1/configs/{project_id} | GET/PUT | 配置管理 |
| /api/v1/scanners | GET | 扫描器列表 |

### 测试触发扫描

```bash
curl -X POST http://localhost:8000/api/v1/scans/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "test_project",
    "repository_url": "https://gitlab.example.com/test/project",
    "branch": "main",
    "commit_sha": "abc123",
    "trigger_type": "manual"
  }'
```

---

## 故障排查

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs app
docker-compose logs mysql

# 实时查看日志
docker-compose logs -f app
```

### 进入容器调试

```bash
# 进入应用容器
docker-compose exec app bash

# 进入MySQL容器
docker-compose exec mysql mysql -u root -p

# 进入Redis容器
docker-compose exec redis redis-cli
```

### 常见问题

| 问题 | 解决方案 |
|------|----------|
| 端口被占用 | 修改.env中的端口配置 |
| MySQL连接失败 | 检查MySQL容器是否正常启动 |
| 应用启动失败 | 查看日志 `docker-compose logs app` |
| 权限问题 | 确保目录权限正确 |

---

## 生产环境建议

### 1. 安全配置

- 修改所有默认密码
- 配置HTTPS（将证书放入nginx/ssl/）
- 限制MySQL只允许内网访问
- 配置防火墙规则

### 2. 性能优化

- 根据服务器配置调整MySQL参数
- 调整Gunicorn worker数量
- 配置Redis持久化
- 启用Nginx缓存

### 3. 监控配置

- 配置Prometheus指标采集
- 设置日志收集（ELK/Loki）
- 配置告警通知

### 4. 备份策略

- 每日自动备份数据库
- 定期清理旧备份
- 测试备份恢复流程
