# CICD_gateway

● GitLab 门禁扫描部署与触发验证指南

  一、整体架构

  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │  GitLab     │────▶│  门禁API    │────▶│  MySQL/Redis│
  │  CI Runner  │     │  Server     │     │  数据库     │
  └─────────────┘     └─────────────┘     └─────────────┘
         │                    │
         │                    ▼
         │             ┌─────────────┐
         └────────────▶│  报告服务器  │
                       │  (Nginx)    │
                       └─────────────┘

  ---
  二、部署门禁API服务

  2.1 服务器环境准备

  # 在目标服务器上执行（如 192.168.3.100）

  # 安装Python 3.10+
  sudo apt update
  sudo apt install python3.10 python3.10-venv python3-pip -y

  # 安装MySQL 8.0
  sudo apt install mysql-server -y
  sudo systemctl start mysql
  sudo systemctl enable mysql

  # 安装Redis
  sudo apt install redis-server -y
  sudo systemctl start redis
  sudo systemctl enable redis

  2.2 创建数据库

  -- 登录MySQL
  mysql -u root -p

  -- 创建数据库和用户
  CREATE DATABASE quality_gate CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  CREATE USER 'gate_user'@'localhost' IDENTIFIED BY 'YourSecurePassword123!';
  GRANT ALL PRIVILEGES ON quality_gate.* TO 'gate_user'@'localhost';
  FLUSH PRIVILEGES;
  EXIT;

  2.3 部署应用代码

  # 克隆代码
  cd /opt
  git clone ssh://git@192.168.3.100:2222/root/qualityGatePlatform.git
  cd qualityGatePlatform

  # 切换到功能分支
  git checkout feat-ai-quality-gate-v1

  # 创建虚拟环境
  python3 -m venv venv
  source venv/bin/activate

  # 安装依赖
  pip install -r requirements.txt
  pip install gunicorn pymysql

  2.4 配置环境变量

  # 创建环境变量文件
  cat > /opt/qualityGatePlatform/.env << 'EOF'
  # 应用配置
  APP_NAME=代码质量门禁系统
  APP_VERSION=1.0.0
  DEBUG=false

  # 数据库配置
  DB_HOST=localhost
  DB_PORT=3306
  DB_USER=gate_user
  DB_PASSWORD=YourSecurePassword123!
  DB_NAME=quality_gate

  # Redis配置
  REDIS_HOST=localhost
  REDIS_PORT=6379
  REDIS_PASSWORD=
  REDIS_DB=0

  # 报告配置
  REPORT_PATH=/var/www/reports
  REPORT_TIMEOUT=60

  # 扫描配置
  SCAN_TIMEOUT=600
  MAX_PARALLEL_GATES=4

  # 通知配置（可选）
  SMTP_HOST=smtp.example.com
  SMTP_PORT=587
  SMTP_USER=alert@example.com
  SMTP_PASSWORD=SmtpPassword123!

  # GitLab配置
  GITLAB_URL=http://192.168.3.200:8090
  GITLAB_TOKEN=your-gitlab-private-token
  EOF

  # 设置权限
  chmod 600 /opt/qualityGatePlatform/.env

  2.5 初始化数据库表

  cd /opt/qualityGatePlatform
  source venv/bin/activate

  # 创建初始化脚本
  cat > init_db.py << 'PYEOF'
  import asyncio
  from src.core.database import init_db

  asyncio.run(init_db())
  print("数据库表创建成功")
  PYEOF

  # 执行初始化
  python init_db.py

  2.6 配置Gunicorn启动

  # 创建Gunicorn配置
  cat > /opt/qualityGatePlatform/gunicorn.conf.py << 'EOF'
  # 绑定地址
  bind = "0.0.0.0:8000"

  # 工作进程数
  workers = 4

  # 工作线程数
  threads = 2

  # 工作模式
  worker_class = "uvicorn.workers.UvicornWorker"

  # 超时时间
  timeout = 120

  # 日志配置
  accesslog = "/var/log/quality-gate/access.log"
  errorlog = "/var/log/quality-gate/error.log"
  loglevel = "info"
  EOF

  # 创建日志目录
  sudo mkdir -p /var/log/quality-gate
  sudo chown $USER:$USER /var/log/quality-gate

  2.7 创建Systemd服务

  # 创建服务文件
  sudo cat > /etc/systemd/system/quality-gate.service << 'EOF'
  [Unit]
  Description=代码质量门禁系统API服务
  After=network.target mysql.service redis.service

  [Service]
  Type=notify
  User=root
  Group=root
  WorkingDirectory=/opt/qualityGatePlatform
  Environment="PATH=/opt/qualityGatePlatform/venv/bin"
  EnvironmentFile=/opt/qualityGatePlatform/.env
  ExecStart=/opt/qualityGatePlatform/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
  ExecReload=/bin/kill -s HUP $MAINPID
  KillMode=mixed
  TimeoutStopSec=5
  PrivateTmp=true
  Restart=always
  RestartSec=5

  [Install]
  WantedBy=multi-user.target
  EOF

  # 启动服务
  sudo systemctl daemon-reload
  sudo systemctl start quality-gate
  sudo systemctl enable quality-gate

  # 检查状态
  sudo systemctl status quality-gate

  2.8 验证服务运行

  # 健康检查
  curl http://localhost:8000/api/v1/health

  # 预期响应：
  # {
  #   "code": 0,
  #   "message": "success",
  #   "data": {
  #     "status": "healthy",
  #     "version": "1.0.0",
  #     "components": {
  #       "database": "healthy",
  #       "cache": "healthy",
  #       "storage": "healthy"
  #     }
  #   }
  # }

  # 测试触发扫描接口
  curl -X POST http://localhost:8000/api/v1/scans/trigger \
    -H "Content-Type: application/json" \
    -d '{
      "project_id": "test_project",
      "repository_url": "https://gitlab.example.com/test/project",
      "branch": "main",
      "commit_sha": "abc123def456",
      "trigger_type": "push"
    }'

  # 预期响应：
  # {
  #   "code": 0,
  #   "message": "success",
  #   "data": {
  #     "scan_id": "scan_20260531_xxxxxxxx",
  #     "status": "pending",
  #     "created_at": "2026-05-31T10:30:00",
  #     "estimated_duration": 300
  #   }
  # }

  ---
  三、配置Nginx反向代理（可选）

  # 创建Nginx配置
  sudo cat > /etc/nginx/sites-available/quality-gate << 'EOF'
  server {
      listen 80;
      server_name quality-gate.example.com;

      # API代理
      location /api/ {
          proxy_pass http://127.0.0.1:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
          proxy_read_timeout 300s;
          proxy_connect_timeout 75s;
      }

      # 报告静态文件
      location /reports/ {
          alias /var/www/reports/;
          autoindex on;
      }
  }
  EOF

  # 启用站点
  sudo ln -s /etc/nginx/sites-available/quality-gate /etc/nginx/sites-enabled/
  sudo nginx -t
  sudo systemctl reload nginx

  ---
  四、配置GitLab CI/CD

  4.1 设置GitLab CI/CD Variables

  在GitLab项目中设置以下变量：

  路径: Settings → CI/CD → Variables

  ┌────────────────────┬───────────────────────────┬──────────────┐
  │       变量名       │            值             │     说明     │
  ├────────────────────┼───────────────────────────┼──────────────┤
  │ QUALITY_GATE_API   │ http://192.168.3.100:8000 │ 门禁API地址  │
  ├────────────────────┼───────────────────────────┼──────────────┤
  │ QUALITY_GATE_TOKEN │ your-api-token            │ API认证Token │
  └────────────────────┴───────────────────────────┴──────────────┘

  4.2 创建 .gitlab-ci.yml

  在项目根目录创建：

  # .gitlab-ci.yml

  stages:
    - build
    - quality-gate
    - deploy

  variables:
    QUALITY_GATE_API: "http://192.168.3.100:8000"

  # ==================== 构建阶段 ====================
  build:
    stage: build
    image: maven:3.8-openjdk-11  # 或其他构建镜像
    script:
      - echo "构建项目..."
      - mvn clean package -DskipTests
    artifacts:
      paths:
        - target/*.jar
    rules:
      - if: '$CI_PIPELINE_SOURCE == "push"'
      - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

  # ==================== 门禁扫描阶段 ====================
  quality_gate_scan:
    stage: quality-gate
    image: alpine:latest
    before_script:
      - apk add --no-cache curl jq
    script:
      - echo "触发门禁扫描..."
      - echo "项目: ${CI_PROJECT_ID}"
      - echo "分支: ${CI_COMMIT_BRANCH}"
      - echo "提交: ${CI_COMMIT_SHA}"
      - echo "触发类型: ${CI_PIPELINE_SOURCE}"

      # 步骤1: 触发门禁扫描
      - |
        SCAN_RESPONSE=$(curl -s -X POST "${QUALITY_GATE_API}/api/v1/scans/trigger" \
          -H "Content-Type: application/json" \
          -H "Authorization: Bearer ${QUALITY_GATE_TOKEN}" \
          -d '{
            "project_id": "'${CI_PROJECT_ID}'",
            "repository_url": "'${CI_REPOSITORY_URL}'",
            "branch": "'${CI_COMMIT_BRANCH}'",
            "commit_sha": "'${CI_COMMIT_SHA}'",
            "trigger_type": "'${CI_PIPELINE_SOURCE}'",
            "merge_request_id": '${CI_MERGE_REQUEST_ID:-null}',
            "metadata": {
              "user": "'${GITLAB_USER_LOGIN}'",
              "project_name": "'${CI_PROJECT_NAME}'"
            }
          }')

        echo "触发响应: ${SCAN_RESPONSE}"

        # 提取scan_id
        SCAN_ID=$(echo "${SCAN_RESPONSE}" | jq -r '.data.scan_id')
        if [ -z "${SCAN_ID}" ] || [ "${SCAN_ID}" = "null" ]; then
          echo "错误: 无法获取scan_id"
          echo "响应: ${SCAN_RESPONSE}"
          exit 1
        fi
        echo "扫描ID: ${SCAN_ID}"

      # 步骤2: 等待扫描完成
      - |
        MAX_WAIT=600
        WAIT_INTERVAL=10
        ELAPSED=0

        echo "等待扫描完成..."

        while [ ${ELAPSED} -lt ${MAX_WAIT} ]; do
          STATUS_RESPONSE=$(curl -s -X GET "${QUALITY_GATE_API}/api/v1/scans/${SCAN_ID}/status" \
            -H "Authorization: Bearer ${QUALITY_GATE_TOKEN}")

          STATUS=$(echo "${STATUS_RESPONSE}" | jq -r '.data.status')
          GATE_PASSED=$(echo "${STATUS_RESPONSE}" | jq -r '.data.gate_passed')

          echo "[${ELAPSED}s] 状态: ${STATUS}, 通过: ${GATE_PASSED}"

          if [ "${STATUS}" = "completed" ]; then
            if [ "${GATE_PASSED}" = "true" ]; then
              echo "=========================================="
              echo "门禁扫描通过 ✅"
              echo "=========================================="
              exit 0
            else
              echo "=========================================="
              echo "门禁扫描失败 ❌"
              echo "=========================================="

              # 显示报告链接
              REPORT_URL=$(echo "${STATUS_RESPONSE}" | jq -r '.data.report_url')
              if [ -n "${REPORT_URL}" ] && [ "${REPORT_URL}" != "null" ]; then
                echo "查看报告: ${REPORT_URL}"
              fi

              # 显示问题摘要
              TOTAL_ISSUES=$(echo "${STATUS_RESPONSE}" | jq -r '.data.summary.total_issues')
              BLOCKING_ISSUES=$(echo "${STATUS_RESPONSE}" | jq -r '.data.summary.blocking_issues')
              echo "问题总数: ${TOTAL_ISSUES}"
              echo "阻断问题: ${BLOCKING_ISSUES}"

              exit 1
            fi
          fi

          if [ "${STATUS}" = "failed" ] || [ "${STATUS}" = "timeout" ]; then
            echo "扫描异常: ${STATUS}"
            ERROR_MSG=$(echo "${STATUS_RESPONSE}" | jq -r '.data.error_message // "未知错误"')
            echo "错误信息: ${ERROR_MSG}"
            exit 1
          fi

          sleep ${WAIT_INTERVAL}
          ELAPSED=$((ELAPSED + WAIT_INTERVAL))
        done

        echo "扫描超时（超过${MAX_WAIT}秒）"
        exit 1

    rules:
      - if: '$CI_PIPELINE_SOURCE == "push"'
        when: always
      - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
        when: always
      - if: '$CI_PIPELINE_SOURCE == "schedule"'
        when: always
    allow_failure: false

  # ==================== 部署阶段（门禁通过后） ====================
  deploy:
    stage: deploy
    image: alpine:latest
    script:
      - echo "门禁通过，开始部署..."
      - echo "部署到目标环境..."
    rules:
      - if: '$CI_COMMIT_BRANCH == "main"'
        when: on_success
    needs:
      - job: quality_gate_scan
        artifacts: false

  4.3 提交配置文件

  # 在项目目录
  git add .gitlab-ci.yml
  git commit -m "ci: 添加门禁扫描CI/CD配置"
  git push origin main

  ---
  五、触发验证流程

  5.1 方式一：Push触发验证

  # 1. 修改代码
  echo "// test gate scan" >> src/Main.java

  # 2. 提交并推送
  git add .
  git commit -m "test: 测试门禁扫描触发"
  git push origin main

  # 3. 在GitLab上查看Pipeline
  # 路径: CI/CD → Pipelines
  # 查看 quality_gate_scan job 的执行日志

  5.2 方式二：MR触发验证

  # 1. 创建功能分支
  git checkout -b feature/test-gate

  # 2. 修改代码
  echo "// test MR gate" >> src/Main.java

  # 3. 提交推送
  git add .
  git commit -m "test: 测试MR门禁扫描"
  git push origin feature/test-gate

  # 4. 在GitLab上创建MR
  # 路径: Merge Requests → New Merge Request
  # 选择 source: feature/test-gate → target: main
  # 创建MR后自动触发Pipeline

  5.3 方式三：手动触发验证

  # 直接调用API测试
  curl -X POST "http://192.168.3.100:8000/api/v1/scans/trigger" \
    -H "Content-Type: application/json" \
    -d '{
      "project_id": "123",
      "repository_url": "ssh://git@192.168.3.100:2222/root/qualityGatePlatform.git",
      "branch": "main",
      "commit_sha": "abc123def456",
      "trigger_type": "manual"
    }'

  ---
  六、查看验证结果

  6.1 GitLab Pipeline日志

  路径: CI/CD → Pipelines → 点击具体Pipeline → quality_gate_scan job

  成功日志示例:
  触发门禁扫描...
  项目: 123
  分支: main
  提交: abc123def456
  触发类型: push
  触发响应: {"code":0,"data":{"scan_id":"scan_20260531_abc123","status":"pending"}}
  扫描ID: scan_20260531_abc123
  等待扫描完成...
  [0s] 状态: pending, 通过: null
  [10s] 状态: running, 通过: null
  [20s] 状态: completed, 通过: true
  ==========================================
  门禁扫描通过 ✅
  ==========================================

  失败日志示例:
  门禁扫描失败 ❌
  查看报告: http://192.168.3.100/reports/view/rpt_20260531_abc123
  问题总数: 5
  阻断问题: 2

  6.2 API查询扫描状态

  # 查询扫描状态
  curl "http://192.168.3.100:8000/api/v1/scans/scan_20260531_abc123/status"

  # 查询报告
  curl "http://192.168.3.100:8000/api/v1/reports/rpt_20260531_abc123"

  # 查询报告列表
  curl "http://192.168.3.100:8000/api/v1/reports?project_id=123&page=1&page_size=10"

  6.3 数据库查询验证

  -- 查询扫描任务
  SELECT scan_id, project_id, trigger_type, scan_status, gate_status,
         total_issues, critical_issues, created_at
  FROM scan_tasks
  ORDER BY created_at DESC
  LIMIT 10;

  -- 查询扫描结果
  SELECT sr.gate_type, sr.execution_status, sr.gate_result,
         sr.total_issues, sr.duration_seconds
  FROM scan_results sr
  WHERE sr.scan_id = 'scan_20260531_abc123';

  -- 查询问题详情
  SELECT severity, file_path, line_number, message, rule_id
  FROM issue_details
  WHERE scan_id = 'scan_20260531_abc123'
  ORDER BY severity, file_path;

  6.4 查看报告页面

  浏览器访问: http://192.168.3.100/reports/view/rpt_20260531_abc123

  ---
  七、故障排查

  7.1 常见问题

  ┌────────────────────┬──────────────┬──────────────────────────────────────────┐
  │        问题        │     原因     │                 解决方案                 │
  ├────────────────────┼──────────────┼──────────────────────────────────────────┤
  │ Connection refused │ 服务未启动   │ sudo systemctl status quality-gate       │
  ├────────────────────┼──────────────┼──────────────────────────────────────────┤
  │ 401 Unauthorized   │ Token错误    │ 检查QUALITY_GATE_TOKEN配置               │
  ├────────────────────┼──────────────┼──────────────────────────────────────────┤
  │ 404 Not Found      │ 路由错误     │ 检查API地址是否正确                      │
  ├────────────────────┼──────────────┼──────────────────────────────────────────┤
  │ 500 Internal Error │ 服务内部错误 │ 查看日志 /var/log/quality-gate/error.log │
  ├────────────────────┼──────────────┼──────────────────────────────────────────┤
  │ 扫描超时           │ 代码库过大   │ 调整SCAN_TIMEOUT配置                     │
  └────────────────────┴──────────────┴──────────────────────────────────────────┘

  7.2 查看服务日志

  # 查看应用日志
  sudo journalctl -u quality-gate -f

  # 查看访问日志
  tail -f /var/log/quality-gate/access.log

  # 查看错误日志
  tail -f /var/log/quality-gate/error.log

  7.3 测试网络连通性

  # 从GitLab Runner测试API连通性
  curl -v http://192.168.3.100:8000/api/v1/health

  # 检查端口是否开放
  nc -zv 192.168.3.100 8000

  ---
  八、验证检查清单

  ┌──────┬───────────────────────┬──────────────────────────────────┐
  │ 步骤 │        检查项         │             验证方法             │
  ├──────┼───────────────────────┼──────────────────────────────────┤
  │ 1    │ API服务正常运行       │ curl /api/v1/health 返回 healthy │
  ├──────┼───────────────────────┼──────────────────────────────────┤
  │ 2    │ 数据库连接正常        │ 健康检查中 database 为 healthy   │
  ├──────┼───────────────────────┼──────────────────────────────────┤
  │ 3    │ GitLab CI变量配置正确 │ Pipeline日志中无认证错误         │
  ├──────┼───────────────────────┼──────────────────────────────────┤
  │ 4    │ Push触发正常          │ 推送代码后Pipeline自动运行       │
  ├──────┼───────────────────────┼──────────────────────────────────┤
  │ 5    │ MR触发正常            │ 创建MR后Pipeline自动运行         │
  ├──────┼───────────────────────┼──────────────────────────────────┤
  │ 6    │ 扫描结果正确上报      │ API返回result_id                 │
  ├──────┼───────────────────────┼──────────────────────────────────┤
  │ 7    │ 报告生成成功          │ 报告URL可访问                    │
  ├──────┼───────────────────────┼──────────────────────────────────┤
  │ 8    │ 门禁阻断生效          │ 失败时MR无法合并                 │
  └──────┴───────────────────────┴──────────────────────────────────┘