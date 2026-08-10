# LexAI 智慧法律智能体平台

<div align="center">

**基于 Spring Boot + Vue 3 + MySQL 的法律 AI 助手平台**，接入腾讯混元大模型（Hunyuan-A13B-Instruct），提供法律咨询、案件分析、合同审查、法律文书生成、合同协议模板检索等功能。

[![Spring Boot 3.2](https://img.shields.io/badge/Spring%20Boot-3.2-6DB33F?style=flat-square&logo=springboot)](https://spring.io/projects/spring-boot)
[![Vue 3](https://img.shields.io/badge/Vue%203-4.x-42B883?style=flat-square&logo=vuedotjs)](https://vuejs.org/)
[![MySQL 8.0](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql)](https://www.mysql.com/)
[![JDK 17](https://img.shields.io/badge/JDK-17-FF6C2C?style=flat-square&logo=openjdk)](https://adoptium.net/)
[![TypeScript](https://img.shields.io/badge/TypeScript-6.x-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-8250DF?style=flat-square)](LICENSE)

</div>

---

## ✨ 功能模块

| 模块 | 说明 |
| --- | --- |
| ⚖️ **法律智能咨询** | AI 问答，支持婚姻家庭、合同纠纷、劳动争议等多个法律分类 |
| 📂 **案件分析** | 用户提交案件描述，AI 自动分析案件类型、诉讼策略与风险点 |
| 📋 **合同审查** | 上传合同文件，基础审查（快速风险点识别）或高级审查（律师级逐条分析） |
| 📄 **法律文书生成** | AI 生成起诉状、答辩状、上诉状等标准法律文书 |
| 📚 **合同协议模板库** | 本地文件系统全文检索，支持关键词搜索、分类浏览和 PDF 预览 |

---

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────────────┐
│                    用户浏览器                          │
│                http://localhost:3000                  │
└─────────────────────┬────────────────────────────────┘
                      │ HTTP
                      ▼
┌──────────────────────────────────────────────────────┐
│            Vite Dev Server（前端）                    │
│        localhost:3000 → Proxy /api/*                 │
└─────────────────────┬────────────────────────────────┘
                      │ /api → :8089
                      ▼
┌──────────────────────────────────────────────────────┐
│           Spring Boot（后端） localhost:8089           │
│  ┌──────────────────────────────────────────────┐   │
│  │  Controllers → Services → Repositories       │   │
│  │  Security（JWT Filter）                        │   │
│  │  AiService（SiliconFlow AI 统一调度）          │   │
│  └──────────────────────────────────────────────┘   │
│          ↓                              ↓              │
│  ┌──────────────┐        ┌──────────────────────┐    │
│  │  MySQL :3306  │        │ SiliconFlow API（外网）│    │
│  │   lexai_db    │        │  腾讯混元 a13b 模型    │    │
│  └──────────────┘        └──────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

| 层级 | 技术选型 |
| --- | --- |
| **前端框架** | Vue 3.4 + TypeScript 6.0 + Vite 5.0 |
| **前端状态** | Pinia 2.1（认证状态管理） |
| **前端路由** | Vue Router 4.2 |
| **HTTP 客户端** | Axios 1.6（统一拦截器，自动注入 JWT） |
| **后端框架** | Spring Boot 3.2 + Java 17 |
| **安全框架** | Spring Security + JWT（jjwt 0.12.3） |
| **持久层** | Spring Data JPA + MySQL 8.0 |
| **AI 接入** | SiliconFlow API（腾讯混元 a13b-instruct） |
| **文档解析** | Apache Tika 2.9.2 |
| **API 文档** | SpringDoc OpenAPI 2.3.0（Swagger UI） |

---

## 🚀 快速开始

### 环境要求

- JDK 17+
- Node.js 18+
- MySQL 8.0+

### 1. 数据库初始化

```bash
mysql -u root -p < database/schema.sql
```

### 2. 后端启动

```bash
cd backend

# 方式一：设置环境变量
export SILICONFLOW_API_KEY=your-api-key
export JWT_SECRET=your-256-bit-secret

# 启动
mvn spring-boot:run
```

> 也可直接修改 `backend/src/main/resources/application.yml` 中的默认值。

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问地址

| 服务 | 地址 |
| --- | --- |
| 🌐 **前端页面** | http://localhost:3000 |
| 🔌 **后端 API** | http://localhost:8089 |
| 📖 **Swagger 文档** | http://localhost:8089/swagger-ui.html |

> 首次使用请访问注册页面（http://localhost:3000/register）创建账号。

---

## 📂 项目结构

```
lexai/
├── backend/                              # Spring Boot 后端
│   └── src/main/java/com/lexai/
│       ├── config/                       # 配置类（CORS、Security、Swagger、SiliconFlow）
│       ├── controller/                   # 控制器层
│       │   ├── AuthController            # 认证（注册/登录）
│       │   ├── ConsultationController    # 法律咨询
│       │   ├── CaseController            # 案件分析
│       │   ├── ContractController        # 合同审查
│       │   ├── DocumentController        # 文书生成
│       │   └── TemplateSearchController  # 模板检索
│       ├── service/                      # 业务逻辑层
│       │   └── AiService                  # AI 调度中心（统一封装 SiliconFlow 调用）
│       ├── repository/                   # JPA 数据访问层
│       ├── entity/                       # 实体类（User, Consultation, Case, Contract, Document, CaseLibrary）
│       ├── dto/                          # 数据传输对象
│       ├── security/                     # JWT 认证（Filter / TokenProvider / UserDetailsService）
│       └── common/                       # 通用响应封装
│
├── frontend/                             # Vue 3 前端
│   └── src/
│       ├── views/                        # 页面组件（9个业务页面）
│       ├── components/                   # 公共组件（TopNavBar、PageHeader、AppLayout 等）
│       ├── stores/                       # Pinia 状态（auth.ts：JWT 认证状态）
│       ├── router/                       # Vue Router（JWT 路由守卫）
│       └── api/                         # Axios 封装（自动注入 Authorization 头）
│
└── database/
    └── schema.sql                        # 数据库建表脚本（JPA 也会自动建表）
```

---

## 🔐 API 认证

- **公开接口**：认证接口 `/api/auth/**`、模板接口 `/api/template/**` 无需认证
- **受保护接口**：其余所有接口需在请求头携带 `Authorization: Bearer <token>`
- JWT Token 登录成功后返回，存储在 localStorage，Axios 拦截器自动注入

---

## 🤖 AI 能力中心

`AiService` 是系统的 AI 调度中心，所有 AI 能力（法律咨询、案件分析、合同审查、文书生成）统一经由它调用 SiliconFlow API。

**合同审查**支持按合同类型选择专属 Prompt：

| 合同类型 | 支持模式 |
| --- | --- |
| 劳动合同 | 基础审查 / 高级审查（律师级） |
| 租赁合同 | 基础审查 / 高级审查（律师级） |
| 买卖合同 | 基础审查 / 高级审查（律师级） |
| 借款合同 | 基础审查 / 高级审查（律师级） |
| 服务合同 | 基础审查 / 高级审查（律师级） |
| 技术合同 | 基础审查 / 高级审查（律师级） |
| 投资合同 | 基础审查 / 高级审查（律师级） |

---

## ⚙️ 核心配置

`backend/src/main/resources/application.yml`

```yaml
server:
  port: 8089

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/lexai_db
    username: root
    password: 123456
  jpa:
    hibernate:
      ddl-auto: update    # 自动创建/更新数据表

siliconflow:
  api:
    key: your-api-key
    base-url: https://api.siliconflow.cn/v1
  model: tencent/hunyuan-a13b-instruct

jwt:
  secret: your-256-bit-secret
  expiration: 86400000   # 24小时

template:
  search:
    root-dir: ../合同协议模板
    max-results: 100000
```

---

## ❓ 常见问题

<details>
<summary><strong>需要申请 API Key 吗？</strong></summary>

是的，需要在 SiliconFlow（https://www.siliconflow.cn）申请 API Key 才能使用 AI 功能。
</details>

<details>
<summary><strong>数据库需要手动建表吗？</strong></summary>

不需要。JPA 配置了 `ddl-auto: update`，启动时会自动创建表结构。也可以执行 `database/schema.sql` 手动初始化。
</details>

<details>
<summary><strong>没有预设账号怎么办？</strong></summary>

系统没有预设账号，请访问 http://localhost:3000/register 注册第一个账号。
</details>

<details>
<summary><strong>前端修改后需要重启吗？</strong></summary>

不需要。Vite 开发服务器支持热模块替换（Hot Module Replacement），修改代码后浏览器会自动刷新。
</details>

---

## 📄 License

本项目采用 [MIT License](LICENSE) 开源。

Copyright © 2026 LexAI.
