---
home: true
layout: false
---

<div align="center">

<img src="frontend/public/brand/logo-original-transparent.png" width="120" height="120" alt="LexAI Logo" style="border-radius: 20px; box-shadow: 0 8px 40px rgba(66,184,131,0.3);">

<h1>
  <span style="font-size: 2.4em; background: linear-gradient(135deg, #42B883, #347a5a); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">LexAI</span>
  <span style="font-size: 0.7em; color: #888; font-weight: 400;">智慧法律智能体平台</span>
</h1>

<p style="font-size: 1.1em; color: #c9d1d9;">
  基于 <strong style="color:#42B883">Spring Boot</strong> +
  <strong style="color:#42B883">Vue 3</strong> +
  <strong style="color:#4479A1">MySQL</strong> 构建，接入
  <strong style="color:#FF6C2C">腾讯混元大模型</strong>的法律 AI 助手
</p>

<p>
  <img src="https://img.shields.io/badge/Spring%20Boot-3.2-6DB33F?style=flat-square&logo=springboot&logoColor=white">
  <img src="https://img.shields.io/badge/Vue%203-4.x-42B883?style=flat-square&logo=vuedotjs&logoColor=white">
  <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white">
  <img src="https://img.shields.io/badge/JDK-17-FF6C2C?style=flat-square&logo=openjdk&logoColor=white">
  <img src="https://img.shields.io/badge/TypeScript-6.x-3178C6?style=flat-square&logo=typescript&logoColor=white">
</p>

<p>
  🌐 <strong>在线体验：</strong><a href="http://58.87.89.131/" target="_blank">http://58.87.89.131/</a>
</p>

<p>
  <a href="#-为什么选择我们">💡 为什么选择我们</a>
  ·
  <a href="#-快速开始">🚀 快速开始</a>
  ·
  <a href="#-功能模块">✨ 功能模块</a>
  ·
  <a href="#-平台截图">📸 平台截图</a>
  ·
  <a href="#-技术架构">🛠️ 技术架构</a>
  ·
  <a href="#-项目结构">📂 项目结构</a>
  ·
  <a href="#-常见问题">❓ 常见问题</a>
  ·
  <a href="README.en.md">🇺🇸 English</a>
</p>

</div>

---

## 💡 为什么选择我们

<div align="center">

| | |
|:---:|:---:|
| ⚡ **免费且无门槛** | 无需注册账号，直接访问 http://58.87.89.131/ 即可使用全部功能，真正零成本体验法律 AI |
| 🤖 **大模型驱动** | 接入腾讯混元大模型（Hunyuan-A13B-Instruct），具备强大的法律语义理解与推理能力 |
| 🔒 **数据安全可信** | 合同文件仅用于 AI 审查分析，不持久化存储，用户数据完全自主 |
| 📱 **随时随地访问** | 基于 Web 端开发，PC / 平板 / 手机均可流畅使用，无需下载安装任何客户端 |
| 📋 **一站式服务** | 从法律咨询、案件分析、合同审查到文书生成，覆盖个人法律需求全流程 |
| 🧩 **操作简单直观** | 对话式交互，无需任何法律背景，上手即用，告别繁琐的表格与流程 |

</div>

---

## 📸 平台截图

<div align="center">

| 首页 | 法律咨询 |
|:---:|:---:|
| <img src="frontend/public/brand/1.png" width="100%" alt="首页"> | <img src="frontend/public/brand/2.png" width="100%" alt="法律咨询"> |

| 案件分析 | 合同模板库 |
|:---:|:---:|
| <img src="frontend/public/brand/3.png" width="100%" alt="案件分析"> | <img src="frontend/public/brand/4.png" width="100%" alt="合同模板库"> |

| 合同审查 | 文书生成 |
|:---:|:---:|
| <img src="frontend/public/brand/5.png" width="100%" alt="合同审查"> | <img src="frontend/public/brand/6.png" width="100%" alt="文书生成"> |

</div>

---

## ✨ 功能模块

### ⚖️ 智慧法律咨询

> 通过自然语言描述法律问题，AI 快速理解并给出专业解答。系统覆盖 **婚姻家庭、继承纠纷、合同纠纷、劳动争议、交通事故、房屋租赁** 等多个法律分类，7×24 小时随时响应，无需预约排队。

| 咨询分类 | 支持状态 |
|---------|---------|
| 婚姻家庭 | 🟢 全功能 |
| 合同纠纷 | 🟢 全功能 |
| 劳动争议 | 🟢 全功能 |
| 交通事故 | 🟢 全功能 |
| 继承纠纷 | 🟢 全功能 |
| 房屋租赁 | 🟢 全功能 |

---

### 📂 案件智能分析

> 提交案件事实描述后，AI 自动完成**案件类型识别、诉讼策略建议、证据清单梳理、风险点评估与法律依据援引**，帮助用户快速把握案件全貌，降低委托律师前的信息门槛。

---

### 📋 合同智能审查

> 上传合同文件（支持 PDF / Word），AI 依据合同类型自动匹配审查规则。支持 **基础审查**（快速风险点识别）与 **高级审查**（律师级逐条分析）两种模式。

| 合同类型 | 基础审查 | 高级审查 |
|----------|:-------:|:-------:|
| 劳动合同 | 🟢 | 🟢 |
| 租赁合同 | 🟢 | 🟢 |
| 买卖合同 | 🟢 | 🟢 |
| 借款合同 | 🟢 | 🟢 |
| 服务合同 | 🟢 | 🟢 |
| 技术合同 | 🟢 | 🟢 |
| 投资合同 | 🟢 | 🟢 |

---

### 📄 法律文书生成

> 根据用户输入的案件信息与诉求，AI 自动生成标准法律文书——**起诉状、答辩状、上诉状、财产保全申请书、强制执行申请书** 等，省去繁琐的格式排版，直接可用于立案。

---

### 📚 合同协议模板库

> 内置本地合同协议模板库，支持 **关键词全文检索与分类浏览**。快速找到与自身需求最匹配的模板，支持在线预览与下载，大幅降低合同起草的初试成本。

---

## 🛠️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                     用户浏览器                             │
│                 http://localhost:3000                    │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Vite Dev Server（前端）                     │
│          localhost:3000 → Proxy /api/*                 │
└──────────────────────────┬──────────────────────────────┘
                           │ /api → :8089
                           ▼
┌─────────────────────────────────────────────────────────┐
│             Spring Boot（后端） localhost:8089            │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Controllers → Services → Repositories           │   │
│  │  Security（JWT Filter）                          │   │
│  │  AiService（SiliconFlow AI 统一调度）            │   │
│  └─────────────────────────────────────────────────┘   │
│              ↓                        ↓                  │
│  ┌───────────────┐       ┌────────────────────────┐    │
│  │  MySQL :3306  │       │ SiliconFlow API（外网）│    │
│  │    lexai_db   │       │  腾讯混元 a13b 模型    │    │
│  └───────────────┘       └────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术选型 |
|------|---------|
| 🖥️ **前端框架** | Vue 3.4 + TypeScript 6.0 + Vite 5.0 |
| 📦 **前端状态** | Pinia 2.1（JWT 认证状态管理） |
| 🧭 **前端路由** | Vue Router 4.2（路由守卫） |
| 🌐 **HTTP 客户端** | Axios 1.6（统一拦截器，自动注入 JWT） |
| ⚙️ **后端框架** | Spring Boot 3.2 + Java 17 |
| 🔐 **安全框架** | Spring Security + JWT（jjwt 0.12.3） |
| 💾 **持久层** | Spring Data JPA + MySQL 8.0 |
| 🤖 **AI 接入** | SiliconFlow API（腾讯混元 a13b-instruct） |
| 📄 **文档解析** | Apache Tika 2.9.2 |
| 📖 **API 文档** | SpringDoc OpenAPI 2.3.0（Swagger UI） |

---

## 🚀 快速开始

### 环境要求

| 工具 | 版本要求 |
|------|---------|
| 🟠 JDK | 17+ |
| 🟢 Node.js | 18+ |
| 🔵 MySQL | 8.0+ |
| 🌐 Git | 最新版 |

### 1. 数据库初始化

```bash
mysql -u root -p < database/schema.sql
```

### 2. 后端启动

```bash
cd backend

# 设置环境变量
export SILICONFLOW_API_KEY=your-api-key
export JWT_SECRET=your-256-bit-secret

# 启动
mvn spring-boot:run
```

> 也可直接修改 `backend/src/main/resources/application.yml` 中的默认配置。

### 3. 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 在线平台 | http://58.87.89.131/ | 在线访问（无需本地部署） |
| 🌐 前端页面 | http://localhost:3000 | 注册/登录后使用全部功能 |
| 🔌 后端 API | http://localhost:8089 | RESTful API 根地址 |
| 📖 Swagger 文档 | http://localhost:8089/swagger-ui.html | API 在线文档 |

---

## 📂 项目结构

```
lexai/
├── backend/                          # Spring Boot 后端
│   └── src/main/java/com/lexai/
│       ├── config/                   # CORS / Security / Swagger / SiliconFlow 配置
│       ├── controller/               # 控制器层
│       │   ├── AuthController        # 认证（注册 / 登录）
│       │   ├── ConsultationController # 法律咨询
│       │   ├── CaseController         # 案件分析
│       │   ├── ContractController     # 合同审查
│       │   ├── DocumentController     # 文书生成
│       │   └── TemplateSearchController # 模板检索
│       ├── service/                  # 业务逻辑层
│       │   └── AiService             # AI 调度中心
│       ├── repository/              # JPA 数据访问层
│       ├── entity/                  # 实体类
│       ├── dto/                    # 数据传输对象
│       ├── security/               # JWT 认证
│       └── common/                 # 通用响应封装
│
├── frontend/                         # Vue 3 前端
│   └── src/
│       ├── views/                   # 页面组件
│       ├── components/             # 公共组件
│       ├── stores/                 # Pinia 状态
│       ├── router/                 # 路由配置
│       └── api/                   # Axios 封装
│
└── database/
    └── schema.sql                   # 数据库建表脚本
```

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
      ddl-auto: update

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

## 🔐 API 认证

- **公开接口**：`/api/auth/**`（认证）、`/api/template/**`（模板）无需认证
- **受保护接口**：其余所有接口需在请求头携带 `Authorization: Bearer <token>`
- JWT Token 存储在 localStorage，Axios 拦截器自动注入

---

## ❓ 常见问题

<details>
<summary><strong>需要申请 API Key 吗？</strong></summary>

是的，需要在 [SiliconFlow](https://www.siliconflow.cn) 申请 API Key 后才能使用 AI 功能。
</details>

<details>
<summary><strong>数据库需要手动建表吗？</strong></summary>

不需要。JPA 配置了 `ddl-auto: update`，启动时会自动创建表结构。也可以执行 `database/schema.sql` 手动初始化。
</details>

<details>
<summary><strong>没有预设账号怎么办？</strong></summary>

系统没有预设账号，请访问 http://58.87.89.131/register 注册第一个账号。
</details>

<details>
<summary><strong>前端修改后需要重启吗？</strong></summary>

不需要。Vite 开发服务器支持热模块替换（Hot Module Replacement），修改代码后浏览器会自动刷新。
</details>

---

<div align="center">

<img src="frontend/public/brand/logo-original-transparent.png" width="60" height="60" alt="LexAI" style="border-radius: 12px;">

**让法律服务触手可及。**

未经许可build，请勿复制、修改。

</div>
