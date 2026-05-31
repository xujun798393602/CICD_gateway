# 代码质量门禁系统 - E2E 验收测试套件

## 文档信息

| 属性 | 值 |
|------|-----|
| 文档标题 | E2E 验收测试套件 |
| 版本 | V1.0 |
| 状态 | 已生成 |
| 生成日期 | 2026-05-31 |
| 需求来源 | doc/requirement/requirement.md |
| 设计来源 | doc/design/tech_design.md |

---

## 1. 覆盖率矩阵

### 1.1 功能点 → 测试用例映射

| 功能点ID | 功能名称 | 正常路径 | 异常路径 | 边界条件 | 集成场景 | 测试用例总数 |
|----------|----------|----------|----------|----------|----------|-------------|
| FR-001 | 代码漏洞扫描 | TC-001-HP-01, TC-001-HP-02, TC-001-HP-03 | TC-001-EP-01, TC-001-EP-02, TC-001-EP-03 | TC-001-EC-01, TC-001-EC-02, TC-001-EC-03 | TC-INT-001 | 10 |
| FR-002 | 代码敏感词扫描 | TC-002-HP-01, TC-002-HP-02, TC-002-HP-03 | TC-002-EP-01, TC-002-EP-02, TC-002-EP-03 | TC-002-EC-01, TC-002-EC-02, TC-002-EC-03 | TC-INT-002 | 10 |
| FR-003 | 代码硬编码扫描 | TC-003-HP-01, TC-003-HP-02, TC-003-HP-03 | TC-003-EP-01, TC-003-EP-02, TC-003-EP-03 | TC-003-EC-01, TC-003-EC-02, TC-003-EC-03 | TC-INT-003 | 10 |
| FR-004 | 代码规范检查 | TC-004-HP-01, TC-004-HP-02, TC-004-HP-03 | TC-004-EP-01, TC-004-EP-02, TC-004-EP-03 | TC-004-EC-01, TC-004-EC-02, TC-004-EC-03 | TC-INT-004 | 10 |
| FR-005 | Push事件触发 | TC-005-HP-01, TC-005-HP-02, TC-005-HP-03 | TC-005-EP-01, TC-005-EP-02 | TC-005-EC-01, TC-005-EC-02, TC-005-EC-03 | TC-INT-005 | 9 |
| FR-006 | MR事件触发 | TC-006-HP-01, TC-006-HP-02, TC-006-HP-03 | TC-006-EP-01, TC-006-EP-02 | TC-006-EC-01, TC-006-EC-02, TC-006-EC-03 | TC-INT-006 | 9 |
| FR-007 | 定时触发 | TC-007-HP-01, TC-007-HP-02, TC-007-HP-03 | TC-007-EP-01, TC-007-EP-02 | TC-007-EC-01, TC-007-EC-02, TC-007-EC-03 | TC-INT-007 | 9 |
| FR-008 | HTML报告生成 | TC-008-HP-01, TC-008-HP-02, TC-008-HP-03 | TC-008-EP-01, TC-008-EP-02, TC-008-EP-03 | TC-008-EC-01, TC-008-EC-02, TC-008-EC-03 | TC-INT-008 | 10 |
| FR-009 | 发送扫描结果通知 | TC-009-HP-01, TC-009-HP-02, TC-009-HP-03 | TC-009-EP-01, TC-009-EP-02, TC-009-EP-03 | TC-009-EC-01, TC-009-EC-02, TC-009-EC-03 | TC-INT-009 | 10 |
| FR-010 | 配置门禁规则 | TC-010-HP-01, TC-010-HP-02, TC-010-HP-03 | TC-010-EP-01, TC-010-EP-02, TC-010-EP-03 | TC-010-EC-01, TC-010-EC-02, TC-010-EC-03 | TC-INT-010 | 10 |
| FR-011 | 插件化门禁扩展 | TC-011-HP-01, TC-011-HP-02, TC-011-HP-03 | TC-011-EP-01, TC-011-EP-02, TC-011-EP-03 | TC-011-EC-01, TC-011-EC-02, TC-011-EC-03 | TC-INT-011 | 10 |
| **总计** | | **33** | **29** | **30** | **11** | **107** |

### 1.2 覆盖率验证

| 维度 | 要求 | 实际 | 状态 |
|------|------|------|------|
| 功能点覆盖率 | 100% | 11/11 = 100% | ✅ 通过 |
| 每功能点正常路径 | ≥1 | 全部≥3 | ✅ 通过 |
| 每功能点异常路径 | ≥2 | 全部≥2 | ✅ 通过 |
| 每功能点边界条件 | ≥1 | 全部≥3 | ✅ 通过 |
| 集成场景覆盖 | 每功能点≥1 | 11/11 = 100% | ✅ 通过 |

---

## 2. FR-001：代码漏洞扫描门禁

### 2.1 正常路径（Happy Path）

#### TC-001-HP-01：代码包含SQL注入漏洞，门禁阻止

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-HP-01 代码包含SQL注入漏洞，门禁阻止
    Given 开发人员向main分支推送代码
    And 代码文件"src/dao/UserDao.java"第45行包含SQL注入漏洞：
      """
      String sql = "SELECT * FROM users WHERE id = " + userId;
      """
    And 漏洞扫描门禁已启用，severity_threshold配置为"high"
    When GitLab检测到Push事件，触发CI流水线
    And CI Job调用POST /api/v1/scans/trigger接口，参数为：
      | 参数         | 值                          |
      | project_id   | proj_001                    |
      | branch       | main                        |
      | trigger_type | push                        |
      | commit_sha   | abc123def456                |
    Then 系统返回scan_id，状态为"pending"
    And 门禁脚本执行完成后，向POST /api/v1/scans/{scan_id}/results上报结果：
      | 参数             | 值                                                                 |
      | scanner_id       | vulnerability_scanner                                              |
      | status           | success                                                            |
      | gate_result      | failed                                                             |
      | total_issues     | 1                                                                  |
      | critical_issues  | 1                                                                  |
    And issue_details表新增1条记录：
      | 字段         | 值                                                      |
      | severity     | critical                                                |
      | file_path    | src/dao/UserDao.java                                    |
      | line_number  | 45                                                      |
      | rule_id      | SQL_INJECTION_001                                       |
      | message      | SQL注入漏洞：直接拼接用户输入构造SQL语句                  |
    And scan_tasks表的gate_status字段为"failed"
    And 流水线状态显示为"失败"
```

#### TC-001-HP-02：代码无漏洞，门禁通过

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-HP-02 代码无漏洞，门禁通过
    Given 开发人员向main分支推送代码
    And 代码文件"src/service/OrderService.java"使用参数化查询：
      """
      String sql = "SELECT * FROM orders WHERE user_id = ?";
      PreparedStatement ps = conn.prepareStatement(sql);
      ps.setString(1, userId);
      """
    And 漏洞扫描门禁已启用
    When GitLab检测到Push事件，触发CI流水线
    And CI Job调用POST /api/v1/scans/trigger接口
    Then 系统返回scan_id，状态为"pending"
    And 门禁脚本执行完成后上报结果，gate_result为"passed"，total_issues为0
    And scan_tasks表的gate_status字段为"passed"
    And 流水线状态显示为"成功"
```

#### TC-001-HP-03：MR代码包含XSS漏洞，门禁阻止合并

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-HP-03 MR代码包含XSS漏洞，门禁阻止合并
    Given 开发人员创建从feature/login到main的MR
    And MR代码文件"src/controller/UserController.java"第78行包含XSS漏洞：
      """
      response.getWriter().write("<div>" + userInput + "</div>");
      """
    When GitLab检测到MR创建事件，触发CI流水线
    And CI Job调用POST /api/v1/scans/trigger接口，trigger_type为"merge_request"，merge_request_id为123
    Then 门禁脚本执行完成后，gate_result为"failed"
    And 系统通过GitLab API更新MR状态为"pipeline failed"
    And MR的"Merge"按钮被禁用，提示"门禁扫描未通过"
```

---

### 2.2 异常路径（Error Path）

#### TC-001-EP-01：扫描工具不可用

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-EP-01 扫描工具不可用
    Given 开发人员向main分支推送代码
    And 漏洞扫描工具未安装或配置错误
    When GitLab检测到Push事件，触发CI流水线
    And 门禁脚本尝试执行漏洞扫描
    Then 脚本返回退出码5（依赖缺失）
    And scan_results表记录：
      | 字段             | 值                         |
      | execution_status | failed                     |
      | exit_code        | 5                          |
      | error_message    | 漏洞扫描工具未安装          |
    And scan_tasks表的skipped_gates字段加1
    And 其他门禁（敏感词、硬编码、代码规范）继续正常执行
    And 系统记录WARNING级别日志，包含scanner_id和错误信息
```

#### TC-001-EP-02：扫描超时

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-EP-02 扫描超时
    Given 开发人员向main分支推送代码
    And 代码库包含大量文件（超过50000行代码）
    And 漏洞扫描门禁的timeout_seconds配置为300秒
    When 门禁脚本执行时间超过300秒
    Then 系统终止脚本执行
    And scan_results表记录：
      | 字段             | 值                                    |
      | execution_status | timeout                               |
      | exit_code        | 3                                     |
      | error_message    | 扫描超时，已超过300秒限制              |
      | duration_seconds | 300                                   |
    And scan_tasks表的gate_status字段为"failed"
    And 流水线状态显示为"失败"
```

#### TC-001-EP-03：扫描工具执行异常

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-EP-03 扫描工具执行异常
    Given 开发人员向main分支推送代码
    And 漏洞扫描工具内部发生未捕获异常
    When 门禁脚本执行过程中崩溃
    Then 脚本返回退出码2（执行错误）
    And scan_results表记录：
      | 字段             | 值                                    |
      | execution_status | failed                                |
      | exit_code        | 2                                     |
      | error_log        | 包含堆栈跟踪信息                      |
    And 系统记录ERROR级别日志
    And 其他门禁继续正常执行
```

---

### 2.3 边界条件（Edge Case）

#### TC-001-EC-01：空代码库扫描

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-EC-01 空代码库扫描
    Given 代码库无任何源代码文件
    When 定时扫描触发，执行漏洞扫描
    Then 门禁脚本正常完成，不报错
    And scan_results表记录：
      | 字段         | 值   |
      | total_issues | 0    |
      | scanned_files| 0    |
      | gate_result  | passed |
    And 报告显示"未发现代码文件，扫描跳过"
```

#### TC-001-EC-02：超大文件扫描

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-EC-02 超大文件扫描
    Given 代码库包含单个超过10MB的Java文件"src/generated/BigFile.java"
    When Push事件触发，执行漏洞扫描
    Then 系统正常扫描该文件，不因文件大小而失败
    And scan_results表的scanned_files字段包含该文件
    And 扫描耗时在合理范围内（不超过timeout_seconds）
```

#### TC-001-EC-03：特殊字符文件名

```gherkin
Feature: FR-001 代码漏洞扫描
  Scenario: TC-001-EC-03 特殊字符文件名
    Given 代码库包含文件名含特殊字符的文件：
      | 文件路径                    |
      | src/模块/用户管理.java      |
      | src/utils/file name.js     |
    When Push事件触发，执行漏洞扫描
    Then 系统正常扫描这些文件
    And HTML报告中正确显示文件路径（UTF-8编码）
    And issue_details表的file_path字段正确存储完整路径
```

---

## 3. FR-002：代码敏感词扫描门禁

### 3.1 正常路径（Happy Path）

#### TC-002-HP-01：代码包含硬编码密码

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-HP-01 代码包含硬编码密码
    Given 开发人员向main分支推送代码
    And 代码文件"src/config/DatabaseConfig.java"第12行包含硬编码密码：
      """
      private String password = "Admin@123456";
      """
    And 敏感词扫描门禁已启用
    When GitLab检测到Push事件，触发CI流水线
    Then 敏感词扫描脚本检测到密码硬编码
    And 向POST /api/v1/scans/{scan_id}/results上报结果：
      | 参数         | 值                                                      |
      | gate_result  | failed                                                   |
      | total_issues | 1                                                        |
    And issue_details表新增记录：
      | 字段        | 值                                    |
      | severity    | critical                              |
      | file_path   | src/config/DatabaseConfig.java        |
      | line_number | 12                                    |
      | issue_type  | hardcoded_password                    |
      | message     | 检测到硬编码密码                       |
    And 敏感信息在报告中脱敏显示为"Admin@***"
```

#### TC-002-HP-02：代码包含API密钥

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-HP-02 代码包含API密钥
    Given 开发人员向main分支推送代码
    And 代码文件"src/service/ThirdPartyClient.java"第34行包含API密钥：
      """
      private String apiKey = "sk-1234567890abcdef";
      """
    When GitLab检测到Push事件，触发CI流水线
    Then 敏感词扫描脚本检测到API密钥
    And gate_result为"failed"
    And issue_details表记录issue_type为"hardcoded_api_key"
    And MR被阻止合并
```

#### TC-002-HP-03：代码无敏感词

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-HP-03 代码无敏感词
    Given 开发人员向main分支推送代码
    And 代码使用环境变量引用敏感信息：
      """
      private String password = System.getenv("DB_PASSWORD");
      """
    When GitLab检测到Push事件，触发CI流水线
    Then 敏感词扫描脚本未检测到敏感信息
    And gate_result为"passed"，total_issues为0
    And 流水线状态显示为"成功"
```

---

### 3.2 异常路径（Error Path）

#### TC-002-EP-01：敏感词库文件缺失

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-EP-01 敏感词库文件缺失
    Given 配置文件中指定的敏感词库路径"config/sensitive-words.txt"不存在
    When Push事件触发，执行敏感词扫描
    Then 系统使用内置默认敏感词库
    And 系统记录WARNING级别日志："敏感词库文件不存在，使用默认词库"
    And 扫描正常完成，不中断
```

#### TC-002-EP-02：敏感词库格式错误

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-EP-02 敏感词库格式错误
    Given 敏感词配置文件"config/sensitive-regex.yml"YAML语法错误
    When Push事件触发，执行敏感词扫描
    Then 系统记录ERROR级别日志："敏感词库解析失败"
    And scan_results表记录：
      | 字段             | 值                        |
      | execution_status | failed                    |
      | error_message    | 敏感词库配置文件格式错误   |
    And gate_result为"failed"
```

#### TC-002-EP-03：正则表达式语法错误

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-EP-03 正则表达式语法错误
    Given 敏感词库中包含无效正则表达式"[invalid(regex"
    When Push事件触发，执行敏感词扫描
    Then 系统跳过该无效正则表达式
    And 系统记录WARNING级别日志，包含具体错误的正则表达式
    And 其他有效规则继续正常执行
    And 扫描正常完成
```

---

### 3.3 边界条件（Edge Case）

#### TC-002-EC-01：注释中的敏感词

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-EC-01 注释中的敏感词
    Given 代码文件包含注释中的敏感词：
      """
      // TODO: 临时密码 password="test123"，后续需要改为环境变量
      """
    When Push事件触发，执行敏感词扫描
    Then 系统检测到敏感词
    And issue_details表记录，metadata中标注"is_comment": true
    And 报告中显示"注释中的敏感信息"分类
```

#### TC-002-EC-02：测试代码中的敏感词

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-EC-02 测试代码中的敏感词
    Given 项目配置文件".quality-gate/config.yml"中配置白名单：
      """
      whitelist:
        sensitive_words:
          - pattern: "test_password"
            reason: "测试环境密码"
            paths: ["**/test/**"]
      """
    And 测试文件"src/test/TestDatabase.java"包含"test_password = 'test123'"
    When Push事件触发，执行敏感词扫描
    Then 系统检测到敏感词，但判定为白名单匹配
    And issue_details表的is_whitelisted字段为true
    And whitelisted_reason字段为"测试环境密码"
    And gate_result为"passed"（白名单问题不阻断）
```

#### TC-002-EC-03：环境变量引用不标记为敏感词

```gherkin
Feature: FR-002 代码敏感词扫描
  Scenario: TC-002-EC-03 环境变量引用不标记为敏感词
    Given 代码文件包含环境变量引用：
      """
      private String dbPassword = "${DB_PASSWORD}";
      private String apiKey = System.getenv("API_KEY");
      """
    And 配置exclude_env_vars为true
    When Push事件触发，执行敏感词扫描
    Then 系统不将环境变量引用标记为敏感词
    And gate_result为"passed"
    And total_issues为0
```

---

## 4. FR-003：代码硬编码扫描门禁

### 4.1 正常路径（Happy Path）

#### TC-003-HP-01：代码包含硬编码IP地址

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-HP-01 代码包含硬编码IP地址
    Given 开发人员向main分支推送代码
    And 代码文件"src/config/ServerConfig.java"第8行包含硬编码IP：
      """
      private String serverHost = "192.168.1.100";
      """
    And 硬编码扫描门禁已启用
    When GitLab检测到Push事件，触发CI流水线
    Then 硬编码扫描脚本检测到IP地址硬编码
    And 向POST /api/v1/scans/{scan_id}/results上报结果：
      | 参数         | 值                                          |
      | gate_result  | failed                                       |
      | total_issues | 1                                             |
    And issue_details表新增记录：
      | 字段        | 值                                    |
      | severity    | medium                                |
      | file_path   | src/config/ServerConfig.java          |
      | line_number | 8                                     |
      | issue_type  | hardcoded_ip_address                  |
      | message     | 检测到硬编码IP地址：192.168.1.100      |
    And 修复建议为"请使用配置文件或环境变量管理IP地址"
```

#### TC-003-HP-02：代码包含硬编码端口号

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-HP-02 代码包含硬编码端口号
    Given 开发人员向main分支推送代码
    And 代码文件"src/service/HttpClient.java"第23行包含硬编码端口：
      """
      int port = 8080;
      """
    When GitLab检测到Push事件，触发CI流水线
    Then 硬编码扫描脚本检测到端口硬编码
    And gate_result为"failed"
    And issue_details表记录issue_type为"hardcoded_port"
```

#### TC-003-HP-03：代码无硬编码

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-HP-03 代码无硬编码
    Given 开发人员向main分支推送代码
    And 代码使用配置文件管理所有可变值：
      """
      private String host = config.getServerHost();
      int port = config.getServerPort();
      """
    When GitLab检测到Push事件，触发CI流水线
    Then 硬编码扫描脚本未检测到硬编码
    And gate_result为"passed"，total_issues为0
    And 流水线状态显示为"成功"
```

---

### 4.2 异常路径（Error Path）

#### TC-003-EP-01：白名单配置错误

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-EP-01 白名单配置错误
    Given 硬编码扫描的白名单配置文件格式错误（非有效YAML）
    When Push事件触发，执行硬编码扫描
    Then 系统忽略错误的白名单配置
    And 系统记录WARNING级别日志："白名单配置解析失败，使用默认规则"
    And 使用默认白名单（127.0.0.1, localhost, 80, 443）继续扫描
```

#### TC-003-EP-02：正则表达式规则错误

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-EP-02 正则表达式规则错误
    Given 硬编码检测规则配置中包含无效正则表达式
    When Push事件触发，执行硬编码扫描
    Then 系统跳过该无效规则
    And 系统记录WARNING级别日志，包含具体错误的规则ID
    And 其他有效规则继续正常执行
    And 扫描正常完成，不中断
```

#### TC-003-EP-03：扫描脚本依赖缺失

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-EP-03 扫描脚本依赖缺失
    Given 硬编码扫描脚本依赖的grep工具版本不兼容
    When Push事件触发，执行硬编码扫描
    Then 脚本返回退出码5（依赖缺失）
    And scan_results表记录execution_status为"failed"
    And error_message为"grep工具版本不兼容，需要3.0+"
    And 其他门禁继续正常执行
```

---

### 4.3 边界条件（Edge Case）

#### TC-003-EC-01：常量定义中的硬编码

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-EC-01 常量定义中的硬编码
    Given 代码文件包含常量定义：
      """
      private static final int MAX_RETRY = 3;
      private static final String DEFAULT_ENCODING = "UTF-8";
      """
    And 配置白名单包含常量定义模式
    When Push事件触发，执行硬编码扫描
    Then 系统根据白名单配置判定常量定义是否为例外
    And 如果配置排除常量定义，则不标记为问题
    And 如果配置不排除，则标记为hardcoded_constant类型
```

#### TC-003-EC-02：配置文件中的硬编码

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-EC-02 配置文件中的硬编码
    Given 配置文件"application.yml"包含IP地址：
      """
      server:
        host: 192.168.1.100
        port: 8080
      """
    And 配置扫描范围排除*.yml文件
    When Push事件触发，执行硬编码扫描
    Then 系统根据配置的扫描范围决定是否扫描配置文件
    And 如果排除配置文件，则不扫描该文件
```

#### TC-003-EC-03：IPv6地址识别

```gherkin
Feature: FR-003 代码硬编码扫描
  Scenario: TC-003-EC-03 IPv6地址识别
    Given 代码文件包含IPv6地址：
      """
      private String host = "::1";
      private String server = "2001:db8::1";
      """
    When Push事件触发，执行硬编码扫描
    Then 系统能够正确识别IPv6地址格式
    And issue_details表记录issue_type为"hardcoded_ipv6_address"
    And 报告中正确显示IPv6地址
```

---

## 5. FR-004：代码规范检查门禁

### 5.1 正常路径（Happy Path）

#### TC-004-HP-01：JavaScript代码不符合ESLint规则

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-HP-01 JavaScript代码不符合ESLint规则
    Given 开发人员向main分支推送JavaScript代码
    And 代码文件"src/utils/helper.js"第15行包含规范问题：
      """
      var x = 1  // 使用var而非let/const，缺少分号
      """
    And ESLint规则配置为"error"级别
    When GitLab检测到Push事件，触发CI流水线
    Then 代码规范检查脚本调用ESLint检测到问题
    And 向POST /api/v1/scans/{scan_id}/results上报结果：
      | 参数         | 值                                          |
      | gate_result  | failed                                       |
      | total_issues | 2                                             |
    And issue_details表新增记录：
      | 字段        | 值                                          |
      | severity    | error                                       |
      | file_path   | src/utils/helper.js                         |
      | line_number | 15                                          |
      | rule_id     | no-var / semi                               |
      | message     | 使用'var'声明变量，请使用'let'或'const'       |
    And gate_result为"failed"（存在Error级别问题）
```

#### TC-004-HP-02：Python代码不符合Pylint规则

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-HP-02 Python代码不符合Pylint规则
    Given 开发人员向main分支推送Python代码
    And 代码文件"src/api/handler.py"第30行包含规范问题：
      """
      def processData( data ):  # 函数名不符合snake_case规范
      """
    When GitLab检测到Push事件，触发CI流水线
    Then 代码规范检查脚本调用Pylint检测到问题
    And issue_details表记录rule_id为"invalid-name(C0103)"
    And gate_result为"failed"
```

#### TC-004-HP-03：代码符合规范

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-HP-03 代码符合规范
    Given 开发人员向main分支推送代码
    And 所有代码文件均符合对应语言的规范要求
    When GitLab检测到Push事件，触发CI流水线
    Then 代码规范检查脚本未检测到Error级别问题
    And gate_result为"passed"，total_issues为0
    And 流水线状态显示为"成功"
```

---

### 5.2 异常路径（Error Path）

#### TC-004-EP-01：ESLint配置文件缺失

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-EP-01 ESLint配置文件缺失
    Given 项目中无.eslintrc.js或.eslintrc.json文件
    When Push事件触发，执行代码规范检查
    Then 系统使用默认ESLint配置
    And 系统记录WARNING级别日志："ESLint配置文件不存在，使用默认配置"
    And 扫描正常完成
```

#### TC-004-EP-02：规范检查工具版本不兼容

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-EP-02 规范检查工具版本不兼容
    Given 项目使用的ESLint版本（9.x）与系统安装的版本（8.x）不兼容
    When Push事件触发，执行代码规范检查
    Then 系统记录ERROR级别日志："ESLint版本不兼容"
    And scan_results表记录execution_status为"failed"
    And error_message为"ESLint版本不兼容，项目需要9.x，当前为8.x"
    And gate_result为"failed"
```

#### TC-004-EP-03：Checkstyle配置文件解析失败

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-EP-03 Checkstyle配置文件解析失败
    Given Java项目的checkstyle.xml配置文件XML语法错误
    When Push事件触发，执行代码规范检查
    Then 系统记录ERROR级别日志："Checkstyle配置文件解析失败"
    And Java文件的规范检查被跳过
    And Python和JavaScript文件的规范检查继续正常执行
```

---

### 5.3 边界条件（Edge Case）

#### TC-004-EC-01：混合语言项目

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-EC-01 混合语言项目
    Given 项目同时包含Java、Python、JavaScript文件：
      | 文件路径              | 语言       |
      | src/main/App.java    | Java       |
      | src/api/server.py    | Python     |
      | src/ui/app.js        | JavaScript |
    When Push事件触发，执行代码规范检查
    Then 系统根据文件扩展名自动选择对应的规范检查工具：
      | 文件模式  | 工具       |
      | *.java    | Checkstyle |
      | *.py      | Pylint     |
      | *.js      | ESLint     |
    And 每种工具独立执行，结果分别上报
```

#### TC-004-EC-02：项目级配置覆盖全局配置

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-EC-02 项目级配置覆盖全局配置
    Given 全局ESLint配置规则"no-console"为"error"
    And 项目级.eslintrc.js配置"no-console"为"warn"
    When Push事件触发，执行代码规范检查
    Then 系统使用项目级配置（"no-console"为"warn"）
    And console.log语句被标记为warning而非error
    And gate_result不受warning级别问题影响
```

#### TC-004-EC-03：排除自动生成的代码文件

```gherkin
Feature: FR-004 代码规范检查
  Scenario: TC-004-EC-03 排除自动生成的代码文件
    Given 项目配置排除自动生成的文件：
      """
      exclude_paths: ["**/generated/**", "**/*.generated.*"]
      """
    And 代码库包含自动生成的文件"src/generated/Proto.java"
    When Push事件触发，执行代码规范检查
    Then 系统跳过自动生成的文件
    And 该文件的规范问题不计入扫描结果
```

---

## 6. FR-005：Push事件触发门禁扫描

### 6.1 正常路径（Happy Path）

#### TC-005-HP-01：单次Push触发扫描

```gherkin
Feature: FR-005 Push事件触发门禁扫描
  Scenario: TC-005-HP-01 单次Push触发扫描
    Given 开发人员向main分支推送代码
    And .gitlab-ci.yml配置了quality-gate stage
    When GitLab检测到Push事件
    Then 自动触发CI Pipeline
    And CI Job调用POST /api/v1/scans/trigger接口
    And 系统创建扫描任务，返回scan_id
    And 所有已启用的门禁脚本被并行执行
    And 扫描完成后，流水线状态正确反映扫描结果
```

#### TC-005-HP-02：批量Push触发扫描

```gherkin
Feature: FR-005 Push事件触发门禁扫描
  Scenario: TC-005-HP-02 批量Push触发扫描
    Given 开发人员一次推送包含5个commit的代码
    And 涉及10个文件的变更
    When GitLab检测到Push事件
    Then 系统触发一次扫描（非每个commit一次）
    And 扫描覆盖所有变更的文件
    And commit_sha记录为最新commit的SHA
```

#### TC-005-HP-03：特定分支触发

```gherkin
Feature: FR-005 Push事件触发门禁扫描
  Scenario: TC-005-HP-03 特定分支触发
    Given .gitlab-ci.yml配置仅对main和develop分支触发：
      """
      rules:
        - if: '$CI_COMMIT_BRANCH == "main"'
        - if: '$CI_COMMIT_BRANCH == "develop"'
      """
    When 开发人员向main分支推送代码
    Then 自动触发CI流水线执行门禁扫描
    When 开发人员向feature/test分支推送代码
    Then 不触发门禁扫描
```

---

### 6.2 异常路径（Error Path）

#### TC-005-EP-01：CI Runner不可用

```gherkin
Feature: FR-005 Push事件触发门禁扫描
  Scenario: TC-005-EP-01 CI Runner不可用
    Given 所有CI Runner处于离线状态
    When 开发人员向main分支推送代码
    Then GitLab检测到Push事件，尝试触发Pipeline
    And Pipeline状态显示为"pending"（等待Runner）
    And 系统记录错误日志："无可用的CI Runner"
    And 开发人员在GitLab界面看到Pipeline挂起状态
```

#### TC-005-EP-02：.gitlab-ci.yml语法错误

```gherkin
Feature: FR-005 Push事件触发门禁扫描
  Scenario: TC-005-EP-02 .gitlab-ci.yml语法错误
    Given .gitlab-ci.yml文件存在YAML语法错误
    When 开发人员推送代码
    Then GitLab报告配置文件语法错误
    And Pipeline状态显示为"failed"
    And 错误信息包含具体语法错误位置
    And 门禁扫描未执行
```

---

### 6.3 边界条件（Edge Case）

#### TC-005-EC-01：强制推送

```gherkin
Feature: FR-005 Push事件触发门禁扫描
  Scenario: TC-005-EC-01 强制推送
    Given 开发人员使用"git push -f"强制推送
    When GitLab检测到Push事件
    Then 系统正常触发扫描
    And 扫描基于最新代码状态（而非diff）
    And commit_sha记录为强制推送后的最新SHA
```

#### TC-005-EC-02：删除分支推送

```gherkin
Feature: FR-005 Push事件触发门禁扫描
  Scenario: TC-005-EC-02 删除分支推送
    Given 开发人员执行"git push origin --delete feature/old-branch"
    When GitLab检测到Push事件
    Then 系统不触发门禁扫描
    And 不创建扫描任务
    And 日志记录"分支删除事件，跳过扫描"
```

#### TC-005-EC-03：标签推送

```gherkin
Feature: FR-005 Push事件触发门禁扫描
  Scenario: TC-005-EC-03 标签推送
    Given 开发人员推送标签"v1.0.0"
    And .gitlab-ci.yml配置标签推送不触发扫描：
      """
      rules:
        - if: '$CI_COMMIT_TAG'
          when: never
      """
    When GitLab检测到Push事件
    Then 系统不触发门禁扫描
```

---

## 7. FR-006：MR事件触发门禁扫描

### 7.1 正常路径（Happy Path）

#### TC-006-HP-01：创建MR触发扫描

```gherkin
Feature: FR-006 MR事件触发门禁扫描
  Scenario: TC-006-HP-01 创建MR触发扫描
    Given 开发人员创建从feature/login到main的MR
    And MR编号为#123
    When GitLab检测到MR创建事件
    Then 自动触发CI Pipeline
    And CI Job调用POST /api/v1/scans/trigger接口：
      | 参数              | 值              |
      | trigger_type      | merge_request   |
      | merge_request_id  | 123             |
      | branch            | feature/login   |
    And 系统创建扫描任务并执行门禁扫描
```

#### TC-006-HP-02：更新MR触发扫描

```gherkin
Feature: FR-006 MR事件触发门禁扫描
  Scenario: TC-006-HP-02 更新MR触发扫描
    Given MR #123已创建，之前的扫描结果为failed
    When 开发人员向MR分支推送新代码修复问题
    Then GitLab检测到MR更新事件
    And 自动触发新的CI Pipeline
    And 重新执行门禁扫描
    And 新的扫描结果覆盖之前的扫描状态
```

#### TC-006-HP-03：门禁通过允许合并

```gherkin
Feature: FR-006 MR事件触发门禁扫描
  Scenario: TC-006-HP-03 门禁通过允许合并
    Given MR #123的门禁扫描全部通过
    And scan_tasks表的gate_status为"passed"
    When 审查人员点击"Merge"按钮
    Then GitLab允许合并操作
    And MR状态变为"Merged"
    And 合并后代码进入目标分支
```

---

### 7.2 异常路径（Error Path）

#### TC-006-EP-01：门禁失败阻止合并

```gherkin
Feature: FR-006 MR事件触发门禁扫描
  Scenario: TC-006-EP-01 门禁失败阻止合并
    Given MR #123的门禁扫描失败
    And scan_tasks表的gate_status为"failed"
    When 审查人员尝试点击"Merge"按钮
    Then GitLab阻止合并操作
    And MR页面显示"Pipeline failed"状态
    And 合并按钮被禁用
    And MR评论中包含门禁失败详情和报告链接
```

#### TC-006-EP-02：合并冲突

```gherkin
Feature: FR-006 MR事件触发门禁扫描
  Scenario: TC-006-EP-02 合并冲突
    Given MR #123存在合并冲突
    When GitLab检测到MR事件
    Then 系统报告合并冲突
    And MR页面显示"Merge conflict"状态
    And 要求开发人员解决冲突后重新推送
    And 门禁扫描在冲突解决前不执行
```

---

### 7.3 边界条件（Edge Case）

#### TC-006-EC-01：MR目标分支变更

```gherkin
Feature: FR-006 MR事件触发门禁扫描
  Scenario: TC-006-EC-01 MR目标分支变更
    Given MR #123最初目标分支为develop
    And 已完成一次门禁扫描
    When 审查人员将目标分支改为main
    Then GitLab检测到MR更新事件
    And 系统根据main分支的门禁配置重新触发扫描
    And 新扫描使用main分支的配置规则
```

#### TC-006-EC-02：大量文件变更的MR

```gherkin
Feature: FR-006 MR事件触发门禁扫描
  Scenario: TC-006-EC-02 大量文件变更的MR
    Given MR #123包含超过1000个文件变更
    When GitLab检测到MR创建事件
    Then 系统正常触发门禁扫描
    And 扫描不因文件数量而失败
    And 扫描耗时在timeout_seconds限制内
```

#### TC-006-EC-03：Draft MR

```gherkin
Feature: FR-006 MR事件触发门禁扫描
  Scenario: TC-006-EC-03 Draft MR
    Given MR #123标记为Draft状态
    And 配置Draft MR不触发扫描
    When GitLab检测到MR创建事件
    Then 系统不触发门禁扫描
    And MR页面显示"Draft - 扫描未触发"
```

---

## 8. FR-007：定时触发门禁扫描

### 8.1 正常路径（Happy Path）

#### TC-007-HP-01：每日定时扫描

```gherkin
Feature: FR-007 定时触发门禁扫描
  Scenario: TC-007-HP-01 每日定时扫描
    Given 全局配置定时扫描计划为每日凌晨2点：
      """
      schedule:
        cron: "0 2 * * *"
        branch: "main"
      """
    And 当前时间为凌晨2:00
    When 定时调度器触发扫描任务
    Then 系统创建扫描任务，trigger_type为"schedule"
    And 扫描main分支的最新代码
    And 执行所有已启用的门禁扫描
    And 扫描完成后自动生成HTML报告
    And 发送扫描结果通知
```

#### TC-007-HP-02：每周定时扫描

```gherkin
Feature: FR-007 定时触发门禁扫描
  Scenario: TC-007-HP-02 每周定时扫描
    Given 全局配置定时扫描计划为每周一凌晨3点：
      """
      schedule:
        cron: "0 3 * * 1"
        branch: "main"
      """
    When 周一凌晨3:00到达
    Then 系统自动触发全量扫描
    And 扫描覆盖整个代码库
    And 生成周报格式的扫描报告
```

#### TC-007-HP-03：手动触发定时扫描

```gherkin
Feature: FR-007 定时触发门禁扫描
  Scenario: TC-007-HP-03 手动触发定时扫描
    Given 管理员需要立即执行一次全量扫描
    When 管理员调用POST /api/v1/scans/trigger接口：
      | 参数         | 值        |
      | trigger_type | manual    |
      | branch       | main      |
    Then 系统立即创建扫描任务
    And 执行全量门禁扫描
    And 扫描完成后生成报告并发送通知
```

---

### 8.2 异常路径（Error Path）

#### TC-007-EP-01：定时任务执行失败

```gherkin
Feature: FR-007 定时触发门禁扫描
  Scenario: TC-007-EP-01 定时任务执行失败
    Given 定时扫描任务触发
    And 扫描过程中数据库连接异常
    When 扫描执行失败
    Then 系统记录ERROR级别日志，包含错误详情
    And scan_tasks表的scan_status为"failed"
    And error_message记录具体错误信息
    And 在下一个扫描周期自动重试
```

#### TC-007-EP-02：定时任务重叠

```gherkin
Feature: FR-007 定时触发门禁扫描
  Scenario: TC-007-EP-02 定时任务重叠
    Given 上一次定时扫描任务仍在执行中
    And 下一次定时扫描时间已到达
    When 定时调度器尝试触发新扫描
    Then 系统检测到已有扫描任务运行中
    And 跳过本次扫描
    And 记录WARNING级别日志："上一次扫描未完成，跳过本次定时扫描"
```

---

### 8.3 边界条件（Edge Case）

#### TC-007-EC-01：跨时区定时扫描

```gherkin
Feature: FR-007 定时触发门禁扫描
  Scenario: TC-007-EC-01 跨时区定时扫描
    Given 服务器时区为UTC
    And 配置定时扫描时间为北京时间凌晨2点（UTC 18:00）
    When UTC时间18:00到达
    Then 系统根据配置的时区执行扫描
    And 扫描时间记录为北京时间凌晨2:00
```

#### TC-007-EC-02：代码库为空

```gherkin
Feature: FR-007 定时触发门禁扫描
  Scenario: TC-007-EC-02 代码库为空
    Given 代码库无任何文件
    When 定时扫描触发
    Then 系统正常完成扫描
    And scan_results表记录scanned_files为0
    And 报告显示"未发现代码文件"
```

#### TC-007-EC-03：服务器重启后恢复

```gherkin
Feature: FR-007 定时触发门禁扫描
  Scenario: TC-007-EC-03 服务器重启后恢复
    Given 门禁系统服务器因维护重启
    And 定时扫描配置为每日凌晨2点
    When 服务器重启完成
    Then 定时调度器自动恢复
    And 下一个凌晨2:00正常触发扫描
    And 重启期间未执行的扫描不补执行
```

---

## 9. FR-008：生成HTML扫描报告

### 9.1 正常路径（Happy Path）

#### TC-008-HP-01：生成通过报告

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-HP-01 生成通过报告
    Given 门禁扫描全部通过
    And scan_tasks表的gate_status为"passed"
    When 所有门禁脚本执行完成
    Then 系统调用POST /api/v1/reports/generate接口
    And 生成HTML格式报告
    And 报告包含扫描概览：
      | 项目         | 值     |
      | 通过状态     | PASSED |
      | 问题总数     | 0      |
      | 扫描时间     | 2026-05-31 10:30:00 |
    And 报告自动部署到Web服务器
    And report_url格式为：https://quality-gate.example.com/reports/view/rpt_{scan_id}
```

#### TC-008-HP-02：生成失败报告

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-HP-02 生成失败报告
    Given 门禁扫描发现多个问题
    And scan_tasks表的total_issues为15，critical_issues为1，high_issues为5
    When 报告生成完成
    Then 报告显示失败状态和问题详情
    And 报告包含按严重级别分组的问题列表
    And 每个问题包含：文件路径、行号、问题类型、严重级别、修复建议
    And 报告支持按门禁类型和严重级别筛选
```

#### TC-008-HP-03：访问报告页面

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-HP-03 访问报告页面
    Given 报告已生成并部署到Web服务器
    And report_url为"https://quality-gate.example.com/reports/view/rpt_20260531_abc123"
    When 用户通过浏览器访问report_url
    Then 浏览器正确显示HTML报告
    And 报告页面支持排序和筛选功能
    And 页面加载时间不超过3秒
```

---

### 9.2 异常路径（Error Path）

#### TC-008-EP-01：报告生成失败

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-EP-01 报告生成失败
    Given 报告模板文件损坏或缺失
    When 系统尝试生成HTML报告
    Then 报告生成失败
    And 系统记录ERROR级别日志："报告模板加载失败"
    And 系统执行降级方案：将扫描结果以JSON格式保存
    And scan_tasks表的report_json字段存储JSON数据
    And 系统记录WARNING级别日志："报告生成失败，已保存JSON格式结果"
```

#### TC-008-EP-02：Web服务器不可用

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-EP-02 Web服务器不可用
    Given 报告Web服务器（Nginx）离线
    When 系统尝试部署报告文件
    Then 部署失败
    And 系统记录ERROR级别日志："报告部署失败，Web服务器不可用"
    And 报告文件保存到本地备份目录
    And scan_tasks表的report_url字段为空
```

#### TC-008-EP-03：磁盘空间不足

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-EP-03 磁盘空间不足
    Given 报告存储磁盘剩余空间不足10MB
    When 系统尝试生成报告
    Then 报告生成失败
    And 系统记录ERROR级别日志："磁盘空间不足"
    And 执行降级方案保存JSON结果
    And 触发告警通知运维人员
```

---

### 9.3 边界条件（Edge Case）

#### TC-008-EC-01：超大报告

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-EC-01 超大报告
    Given 扫描发现超过10000个问题
    When 系统生成HTML报告
    Then 报告正常生成，不因数据量大而失败
    And 报告支持分页显示，每页显示50条记录
    And 报告页面支持客户端筛选和排序
    And 报告文件大小在合理范围内（不超过50MB）
```

#### TC-008-EC-02：特殊字符问题描述

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-EC-02 特殊字符问题描述
    Given 问题描述包含HTML特殊字符：
      """
      <script>alert('xss')</script> & "quotes"
      """
    When 系统生成HTML报告
    Then 系统正确转义特殊字符为HTML实体
    And 报告正常显示，不执行JavaScript
    And 问题描述在报告中正确展示原文
```

#### TC-008-EC-03：并发访问报告

```gherkin
Feature: FR-008 生成HTML扫描报告
  Scenario: TC-008-EC-03 并发访问报告
    Given 报告已部署到Web服务器
    When 100个用户同时访问同一报告URL
    Then Web服务器正常响应所有请求
    And 所有用户看到一致的报告内容
    And 平均响应时间不超过2秒
```

---

## 10. FR-009：发送扫描结果通知

### 10.1 正常路径（Happy Path）

#### TC-009-HP-01：邮件通知失败结果

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-HP-01 邮件通知失败结果
    Given 门禁扫描失败
    And 通知配置启用邮件通知：
      """
      notifications:
        channels:
          email:
            enabled: true
            recipients:
              - type: "submitter"
      """
    When 扫描完成
    Then 系统调用POST /api/v1/notifications/send接口
    And 系统向代码提交者发送邮件通知
    And 邮件内容包含：
      | 项目         | 内容                                    |
      | 主题         | [门禁失败] project-001 main分支扫描结果  |
      | 正文         | 扫描结果摘要（通过/失败、问题数量）       |
      | 报告链接     | https://quality-gate.example.com/reports/view/rpt_xxx |
    And notification_logs表记录发送状态为"sent"
```

#### TC-009-HP-02：MR评论通知

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-HP-02 MR评论通知
    Given MR #123的门禁扫描失败
    And 通知配置启用GitLab MR评论通知
    When 扫描完成
    Then 系统通过GitLab API在MR #123上添加评论
    And 评论内容为Markdown格式：
      """
      ## 门禁扫描结果：❌ 未通过

      | 门禁类型 | 结果 | 问题数 |
      |----------|------|--------|
      | 漏洞扫描 | ❌   | 3      |
      | 敏感词   | ✅   | 0      |

      [查看完整报告](https://quality-gate.example.com/reports/view/rpt_xxx)
      """
    And notification_logs表记录notification_type为"gitlab_comment"
```

#### TC-009-HP-03：通过时发送通知

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-HP-03 通过时发送通知
    Given 门禁扫描全部通过
    And 通知配置启用通过时通知：
      """
      notifications:
        conditions:
          on_success: true
      """
    When 扫描完成
    Then 系统向相关人员发送通过通知
    And 通知内容包含"门禁扫描通过"和报告链接
```

---

### 10.2 异常路径（Error Path）

#### TC-009-EP-01：邮件发送失败

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-EP-01 邮件发送失败
    Given 邮件服务器（SMTP）不可用
    When 系统尝试发送邮件通知
    Then 邮件发送失败
    And notification_logs表记录：
      | 字段         | 值                          |
      | send_status  | retry                       |
      | retry_count  | 1                           |
      | error_message| SMTP连接超时                |
    And 系统等待5秒后自动重试
    And 重试3次后仍失败，send_status更新为"failed"
    And 记录ERROR级别日志
```

#### TC-009-EP-02：GitLab API调用失败

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-EP-02 GitLab API调用失败
    Given GitLab API不可用或返回500错误
    When 系统尝试发送MR评论通知
    Then API调用失败
    And notification_logs表记录send_status为"retry"
    And 系统自动重试3次，每次间隔5秒
    And 3次重试后仍失败，记录为"failed"
    And 不影响邮件通知的发送
```

#### TC-009-EP-03：通知配置缺失

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-EP-03 通知配置缺失
    Given 项目未配置通知设置
    When 扫描完成
    Then 系统使用默认通知配置
    And 默认仅向代码提交者发送邮件通知
    And 记录INFO级别日志："使用默认通知配置"
```

---

### 10.3 边界条件（Edge Case）

#### TC-009-EC-01：提交者邮箱不存在

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-EC-01 提交者邮箱不存在
    Given 代码提交者在GitLab中未配置邮箱
    When 系统尝试发送邮件通知
    Then 系统无法获取提交者邮箱
    And 记录WARNING级别日志："提交者邮箱不存在，跳过邮件通知"
    And 尝试通过其他配置的接收人发送通知
    And notification_logs表记录send_status为"skipped"
```

#### TC-009-EC-02：通知内容过长

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-EC-02 通知内容过长
    Given 扫描发现超过500个问题
    And 通知内容超过邮件正文限制（65535字符）
    When 系统生成通知内容
    Then 系统截断通知内容
    And 在末尾添加"更多详情请查看完整报告"提示
    And 截断后的内容包含报告链接
```

#### TC-009-EC-03：重复通知去重

```gherkin
Feature: FR-009 发送扫描结果通知
  Scenario: TC-009-EC-03 重复通知去重
    Given 同一扫描任务因网络原因触发多次通知请求
    When 系统检测到重复通知
    Then 系统去重，避免向同一接收人发送重复通知
    And notification_logs表中同一scan_id和recipient只有一条记录
```

---

## 11. FR-010：配置门禁规则

### 11.1 正常路径（Happy Path）

#### TC-010-HP-01：修改全局配置

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-HP-01 修改全局配置
    Given 管理员需要修改全局门禁配置
    When 管理员调用PUT /api/v1/configs/_global接口：
      """
      {
        "config": {
          "gates": {
            "vulnerability": {
              "timeout_seconds": 600
            }
          }
        },
        "comment": "增加漏洞扫描超时时间"
      }
      """
    Then 系统更新全局配置
    And 返回新的config_version
    And 后续扫描使用新配置
    And 配置变更记录在版本控制中
```

#### TC-010-HP-02：修改项目配置

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-HP-02 修改项目配置
    Given 项目proj_001需要自定义配置
    When 项目成员调用PUT /api/v1/configs/proj_001接口：
      """
      {
        "config": {
          "gates": {
            "hardcode": {
              "enabled": false
            },
            "vulnerability": {
              "severity_threshold": "critical"
            }
          }
        }
      }
      """
    Then 系统创建项目级配置
    And 项目级配置覆盖全局配置
    And 查询时使用merged=true返回合并后的配置
```

#### TC-010-HP-03：使用默认配置

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-HP-03 使用默认配置
    Given 项目proj_new无自定义配置
    When 项目执行门禁扫描
    Then 系统查询项目配置，未找到
    And 系统使用全局默认配置
    And 记录INFO级别日志："使用全局默认配置"
```

---

### 11.2 异常路径（Error Path）

#### TC-010-EP-01：配置文件语法错误

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-EP-01 配置文件语法错误
    Given 配置文件YAML语法错误
    When 扫描执行时加载配置
    Then 系统记录ERROR级别日志："配置文件解析失败"
    And 系统使用默认配置继续执行扫描
    And 返回错误码40001（参数验证失败）
```

#### TC-010-EP-02：配置项值无效

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-EP-02 配置项值无效
    Given 配置文件中timeout_seconds设置为-1
    When 扫描执行时加载配置
    Then 系统记录WARNING级别日志："timeout_seconds值无效，使用默认值600"
    And 使用默认值600秒继续执行
```

#### TC-010-EP-03：配置版本冲突

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-EP-03 配置版本冲突
    Given 两个管理员同时修改同一项目配置
    And 管理员A基于config_version="1.2.0"提交更新
    And 管理员B也基于config_version="1.2.0"提交更新
    When 管理员B的更新请求到达
    Then 系统检测到版本冲突
    And 返回错误码40901（资源冲突）
    And 错误信息为"配置已被修改，请重新获取最新配置"
```

---

### 11.3 边界条件（Edge Case）

#### TC-010-EC-01：配置文件为空

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-EC-01 配置文件为空
    Given 项目配置文件内容为空（0字节）
    When 扫描执行时加载配置
    Then 系统使用全局默认配置
    And 记录WARNING级别日志："项目配置文件为空"
```

#### TC-010-EC-02：配置文件编码问题

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-EC-02 配置文件编码问题
    Given 配置文件使用GBK编码（非UTF-8）
    When 扫描执行时加载配置
    Then 系统尝试自动检测编码
    And 如果检测成功，正常解析配置
    And 如果检测失败，记录ERROR日志并使用默认配置
```

#### TC-010-EC-03：配置文件权限问题

```gherkin
Feature: FR-010 配置门禁规则
  Scenario: TC-010-EC-03 配置文件权限问题
    Given 配置文件无读取权限（chmod 000）
    When 扫描执行时加载配置
    Then 系统记录ERROR级别日志："配置文件无读取权限"
    And 系统使用默认配置继续执行
```

---

## 12. FR-011：插件化门禁扩展

### 12.1 正常路径（Happy Path）

#### TC-011-HP-01：添加新门禁脚本

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-HP-01 添加新门禁脚本
    Given 开发人员编写新的门禁脚本"custom-security-scan.sh"
    And 脚本遵循统一接口规范：
      - 通过环境变量接收输入（QUALITY_GATE_SCAN_ID等）
      - 通过标准输出返回JSON格式结果
      - 遵循退出码规范（0通过、1失败、2错误、3超时）
    And 脚本放置在"scripts/"目录下
    When 开发人员调用POST /api/v1/scanners/register接口注册：
      """
      {
        "scanner_id": "custom_security_scanner",
        "name": "自定义安全扫描器",
        "version": "1.0.0",
        "category": "custom",
        "entry_point": "scripts/custom-security-scan.sh"
      }
      """
    Then 系统注册新扫描器
    And 后续扫描自动识别并执行新门禁脚本
```

#### TC-011-HP-02：禁用门禁脚本

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-HP-02 禁用门禁脚本
    Given 管理员需要临时禁用某个门禁
    When 管理员更新配置：
      """
      gates:
        hardcode:
          enabled: false
      """
    Then 后续扫描跳过硬编码扫描门禁
    And scan_tasks表的skipped_gates字段加1
    And 其他门禁继续正常执行
```

#### TC-011-HP-03：新脚本集成报告

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-HP-03 新脚本集成报告
    Given 新门禁脚本"custom_security_scanner"已注册并执行完成
    When 系统生成HTML报告
    Then 新门禁扫描结果自动集成到统一报告中
    And 报告中显示新的门禁类型和扫描结果
    And 覆盖率矩阵包含新门禁的统计
```

---

### 12.2 异常路径（Error Path）

#### TC-011-EP-01：脚本不符合规范

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-EP-01 脚本不符合规范
    Given 新门禁脚本未遵循输出JSON格式规范
    And 脚本输出为纯文本而非JSON
    When 扫描执行时调用该脚本
    Then 系统无法解析脚本输出
    And 记录ERROR级别日志："脚本输出格式错误，期望JSON格式"
    And scan_results表记录execution_status为"failed"
    And 该门禁被标记为失败
    And 其他门禁继续正常执行
```

#### TC-011-EP-02：脚本执行权限问题

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-EP-02 脚本执行权限问题
    Given 门禁脚本文件无执行权限（chmod 644）
    When 扫描执行时调用该脚本
    Then 系统无法执行脚本
    And 记录ERROR级别日志："脚本无执行权限"
    And scan_results表记录execution_status为"failed"
    And error_message为"Permission denied"
```

#### TC-011-EP-03：脚本返回错误退出码

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-EP-03 脚本返回错误退出码
    Given 门禁脚本执行过程中发生错误
    And 脚本返回退出码2（执行错误）
    When 扫描执行完成
    Then scan_results表记录：
      | 字段             | 值           |
      | execution_status | failed       |
      | exit_code        | 2            |
    And 系统记录脚本的stderr输出到error_log字段
    And 其他门禁继续正常执行
```

---

### 12.3 边界条件（Edge Case）

#### TC-011-EC-01：同名脚本冲突

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-EC-01 同名脚本冲突
    Given 两个不同目录下存在同名脚本：
      | 路径                          | 版本  |
      | scripts/v1/vulnerability-scan.sh | 1.0   |
      | scripts/v2/vulnerability-scan.sh | 2.0   |
    When 扫描执行时
    Then 系统记录WARNING级别日志："发现同名脚本，使用第一个发现的"
    And 使用按目录优先级排序的第一个脚本
    And 日志中记录使用的脚本路径
```

#### TC-011-EC-02：脚本依赖缺失

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-EC-02 脚本依赖缺失
    Given 门禁脚本依赖的工具（如semgrep）未安装
    When 扫描执行时调用该脚本
    Then 脚本返回退出码5（依赖缺失）
    And scan_results表记录：
      | 字段             | 值                           |
      | execution_status | failed                       |
      | exit_code        | 5                            |
      | error_message    | 依赖工具semgrep未安装         |
    And 其他门禁继续正常执行
```

#### TC-011-EC-03：脚本超时

```gherkin
Feature: FR-011 插件化门禁扩展
  Scenario: TC-011-EC-03 脚本超时
    Given 门禁脚本执行时间超过配置的timeout_seconds
    When 超时发生
    Then 系统终止脚本执行
    And 脚本返回退出码3（超时）
    And scan_results表记录execution_status为"timeout"
    And duration_seconds记录实际执行时间
    And 系统记录WARNING级别日志
```

---

## 13. 集成场景测试

### TC-INT-001：完整Push触发漏洞扫描流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-001 完整Push触发漏洞扫描流程
    Given 开发人员向main分支推送包含SQL注入漏洞的代码
    And 门禁配置启用漏洞扫描，severity_threshold为"high"
    When GitLab CI Pipeline触发
    Then 完整流程为：
      | 步骤 | 操作                                           | 预期结果                    |
      | 1    | CI Job调用POST /api/v1/scans/trigger            | 返回scan_id，状态pending    |
      | 2    | 系统创建scan_tasks记录                          | scan_status为pending        |
      | 3    | 门禁脚本执行漏洞扫描                            | 扫描完成                    |
      | 4    | 脚本调用POST /api/v1/scans/{scan_id}/results    | 返回result_id               |
      | 5    | 系统更新scan_tasks和scan_results                | gate_status为failed         |
      | 6    | 系统生成HTML报告                                | report_url已生成            |
      | 7    | CI Pipeline状态更新为failed                     | 流水线失败                  |
    And 所有数据库记录一致
    And 报告内容与扫描结果一致
```

### TC-INT-002：完整MR触发敏感词扫描流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-002 完整MR触发敏感词扫描流程
    Given 开发人员创建MR，代码包含硬编码API密钥
    And 通知配置启用邮件和MR评论通知
    When GitLab MR事件触发
    Then 完整流程为：
      | 步骤 | 操作                                           | 预期结果                    |
      | 1    | CI Job调用POST /api/v1/scans/trigger            | 返回scan_id                 |
      | 2    | 敏感词扫描脚本执行                              | 检测到API密钥               |
      | 3    | 脚本上报扫描结果                                | gate_result为failed         |
      | 4    | 系统更新MR状态                                  | MR显示pipeline failed       |
      | 5    | 系统发送邮件通知                                | 提交者收到邮件              |
      | 6    | 系统添加MR评论                                  | MR页面显示门禁结果          |
      | 7    | MR合并被阻止                                    | Merge按钮禁用               |
```

### TC-INT-003：完整硬编码扫描流程（含白名单）

```gherkin
Feature: 集成场景
  Scenario: TC-INT-003 完整硬编码扫描流程（含白名单）
    Given 代码包含硬编码IP"192.168.1.100"
    And 白名单配置排除"127.0.0.1"和"localhost"
    When Push触发扫描
    Then 扫描检测到硬编码IP
    And IP"192.168.1.100"不在白名单中，标记为问题
    And 报告中显示问题详情和修复建议
```

### TC-INT-004：完整代码规范检查流程（混合语言）

```gherkin
Feature: 集成场景
  Scenario: TC-INT-004 完整代码规范检查流程（混合语言）
    Given 项目包含Java、Python、JavaScript文件
    And 各语言规范检查工具已配置
    When Push触发扫描
    Then Checkstyle检查Java文件
    And Pylint检查Python文件
    And ESLint检查JavaScript文件
    And 所有结果汇总到统一报告
    And 各工具独立执行，互不影响
```

### TC-INT-005：Push触发后完整报告生成流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-005 Push触发后完整报告生成流程
    Given Push触发扫描，发现多种类型问题
    When 扫描完成
    Then 系统生成HTML报告
    And 报告部署到Web服务器
    And 更新scan_tasks表的report_url
    And 用户可通过URL访问报告
    And 报告支持按门禁类型和严重级别筛选
```

### TC-INT-006：MR触发后门禁阻止合并流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-006 MR触发后门禁阻止合并流程
    Given MR触发扫描，门禁失败
    When 扫描完成
    Then MR状态更新为pipeline failed
    And MR评论中包含门禁结果摘要和报告链接
    And Merge按钮被禁用
    And 开发人员修复问题后推送新代码
    And 新扫描触发，门禁通过
    And MR状态更新为pipeline passed
    And Merge按钮启用
```

### TC-INT-007：定时触发后通知发送流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-007 定时触发后通知发送流程
    Given 定时扫描配置为每日凌晨2点
    When 定时任务触发
    Then 执行全量扫描
    And 生成扫描报告
    And 发送邮件通知给配置的接收人
    And 通知内容包含报告链接
    And notification_logs表记录发送结果
```

### TC-INT-008：报告生成失败降级流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-008 报告生成失败降级流程
    Given 扫描完成，但报告模板损坏
    When 系统尝试生成报告
    Then HTML报告生成失败
    And 系统执行降级方案
    And 扫描结果以JSON格式保存到scan_tasks.report_json
    And 记录WARNING日志
    And 用户可通过API查询JSON格式结果
```

### TC-INT-009：通知失败重试流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-009 通知失败重试流程
    Given 扫描完成，需要发送通知
    And 邮件服务器暂时不可用
    When 第一次邮件发送失败
    Then notification_logs表记录retry_count=1，send_status=retry
    And 系统等待5秒后重试
    And 第二次发送成功
    And notification_logs表更新send_status=sent
```

### TC-INT-010：配置更新后立即生效流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-010 配置更新后立即生效流程
    Given 管理员更新项目配置，禁用硬编码扫描
    When 配置更新API调用成功
    And 新的Push触发扫描
    Then 扫描使用最新配置
    And 硬编码扫描被跳过（skipped_gates+1）
    And 其他门禁正常执行
    And 配置变更无需重新部署
```

### TC-INT-011：新门禁插件完整集成流程

```gherkin
Feature: 集成场景
  Scenario: TC-INT-011 新门禁插件完整集成流程
    Given 开发人员编写新的安全扫描脚本
    When 注册新扫描器到系统
    Then 新扫描器出现在GET /api/v1/scanners列表中
    And Push触发扫描时自动执行新脚本
    And 新脚本结果集成到HTML报告
    And 可通过配置启用/禁用新脚本
```

---

## 14. 非功能性需求测试

### 14.1 性能测试

| 测试ID | 测试场景 | 验收标准 | 关联NFR |
|--------|----------|----------|---------|
| TC-PERF-001 | 单文件扫描时间 | 单文件扫描时间不超过30秒 | NFR-001 |
| TC-PERF-002 | 整体扫描时间 | 10万行代码库完整扫描不超过10分钟 | NFR-002 |
| TC-PERF-003 | 并发扫描能力 | 支持同时执行至少5个项目的扫描 | NFR-003 |
| TC-PERF-004 | 报告生成时间 | 报告生成不超过1分钟 | NFR-004 |
| TC-PERF-005 | 定时扫描资源占用 | 定时扫描期间CPU占用不超过80% | NFR-005 |

### 14.2 安全测试

| 测试ID | 测试场景 | 验收标准 | 关联NFR |
|--------|----------|----------|---------|
| TC-SEC-001 | GitLab凭证管理 | 凭证存储在CI/CD Variables中 | NFR-006 |
| TC-SEC-002 | 报告访问控制 | 报告支持GitLab身份认证 | NFR-007 |
| TC-SEC-003 | 敏感信息脱敏 | 密码密钥显示为*** | NFR-008 |
| TC-SEC-004 | 脚本执行隔离 | 脚本在隔离容器中执行 | NFR-009 |
| TC-SEC-005 | 配置文件安全 | 敏感配置使用环境变量 | NFR-010 |

### 14.3 可靠性测试

| 测试ID | 测试场景 | 验收标准 | 关联NFR |
|--------|----------|----------|---------|
| TC-REL-001 | 扫描工具不可用 | 单个门禁失败不影响其他门禁 | NFR-011 |
| TC-REL-002 | 扫描超时 | 超时后终止并标记失败 | NFR-012 |
| TC-REL-003 | 重试机制 | 网络失败自动重试3次 | NFR-013 |
| TC-REL-004 | 报告生成失败 | JSON降级方案 | NFR-014 |
| TC-REL-005 | 定时扫描容错 | 失败时下一周期重试 | NFR-015 |

---

## 15. 测试用例统计

| 类别 | 数量 |
|------|------|
| 正常路径（Happy Path） | 33 |
| 异常路径（Error Path） | 29 |
| 边界条件（Edge Case） | 30 |
| 集成场景（Integration） | 11 |
| 非功能性测试 | 15 |
| **总计** | **118** |

---

## 16. 测试数据说明

### 16.1 测试项目配置

| 项目ID | 项目名称 | 说明 |
|--------|----------|------|
| proj_001 | 测试项目A | Java项目，完整配置 |
| proj_002 | 测试项目B | Python项目，默认配置 |
| proj_003 | 测试项目C | 混合语言项目 |
| proj_new | 新项目 | 无自定义配置 |

### 16.2 测试用户

| 用户ID | 角色 | 说明 |
|--------|------|------|
| user_dev1 | 开发人员 | 代码提交者 |
| user_dev2 | 开发人员 | MR创建者 |
| user_reviewer | 审查人员 | MR审查者 |
| user_admin | 管理员 | 配置管理员 |

### 16.3 API测试Token

| Token | 权限 | 说明 |
|-------|------|------|
| QUALITY_GATE_TOKEN | 读写 | CI/CD集成Token |
| ADMIN_TOKEN | 管理 | 管理员Token |
| READONLY_TOKEN | 只读 | 只读访问Token |

---

## 附录：修订历史

| 版本 | 日期 | 修订内容 | 作者 |
|------|------|----------|------|
| V1.0 | 2026-05-31 | 初始版本，生成完整验收测试套件 | 测试用例生成器 |
