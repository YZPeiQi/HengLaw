# LexAI 智慧法律智能体平台

<p align="center">
  <img src="frontend/public/brand/logo-original-transparent.png" width="120" alt="LexAI Logo" />
</p>

<p align="center">
  <strong>接入腾讯混元大模型的法律 AI 助手平台</strong><br>
  法律咨询 · 案件分析 · 合同审查 · 文书生成 · 模板检索
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/Spring%20Boot-3.2-6DB33F?style=flat-square&logo=springboot"></a>
  <a href="#"><img src="https://img.shields.io/badge/Vue%203-4.x-42B883?style=flat-square&logo=vuedotjs"></a>
  <a href="#"><img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql"></a>
  <a href="#"><img src="https://img.shields.io/badge/JDK-17-FF6C2C?style=flat-square&logo=openjdk"></a>
  <a href="#"><img src="https://img.shields.io/badge/TypeScript-6.x-3178C6?style=flat-square&logo=typescript"></a>
  <a href="#"><img src="https://img.shields.io/badge/License-MIT-8250DF?style=flat-square"></a>
</p>

---

## 平台概览

LexAI 是一款专为个人用户及小微企业打造的**一站式法律 AI 平台**，基于 Spring Boot + Vue 3 + MySQL 架构，接入**腾讯混元大模型（Hunyuan-A13B-Instruct）**，为用户提供专业、便捷、免费的法律服务。

---

## 功能模块

### 智慧法律咨询
<div class="feature-card">

用户通过自然语言描述法律问题，AI 快速理解并给出专业解答。系统覆盖婚姻家庭、继承纠纷、合同纠纷、劳动争议、交通事故、房屋租赁等**多个法律分类**，7×24 小时随时响应，无需预约排队。

</div>

### 案件智能分析
<div class="feature-card">

提交案件事实描述后，AI 自动完成案件类型识别、诉讼策略建议、证据清单梳理、风险点评估与法律依据援引，帮助用户快速把握案件全貌，降低委托律师前的信息门槛。

</div>

### 合同智能审查
<div class="feature-card">

上传合同文件（支持 PDF/Word），AI 依据合同类型自动匹配审查规则。支持**基础审查**（快速风险点识别）与**高级审查**（律师级逐条分析）两种模式，涵盖劳动合同、租赁合同、买卖合同、借款合同、服务合同、技术合同、投资合同等类型。

</div>

### 法律文书生成
<div class="feature-card">

根据用户输入的案件信息与诉求，AI 自动生成标准法律文书，包括起诉状、答辩状、上诉状、财产保全申请书、强制执行申请书等，省去繁琐的格式排版，直接可用于立案。

</div>

### 合同协议模板库
<div class="feature-card">

内置本地合同协议模板库，支持关键词全文检索与分类浏览。用户可快速找到与自身需求最匹配的模板，并支持在线预览与下载，大幅降低合同起草的初试成本。

</div>

---

## 平台截图

<div align="center">

### 首页
<img src="frontend/public/brand/1.png" width="90%" alt="首页" />

### 法律咨询
<img src="frontend/public/brand/2.png" width="90%" alt="法律咨询" />

### 案件分析
<img src="frontend/public/brand/3.png" width="90%" alt="案件分析" />

### 合同模板库
<img src="frontend/public/brand/4.png" width="90%" alt="合同模板库" />

### 合同审查
<img src="frontend/public/brand/5.png" width="90%" alt="合同审查" />

### 文书生成
<img src="frontend/public/brand/6.png" width="90%" alt="文书生成" />

</div>

---

## 技术架构

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
│  ┌─────────────────────────────────────────────────┐    │
│  │  Controllers → Services → Repositories           │    │
│  │  Security（JWT Filter）                          │    │
│  │  AiService（SiliconFlow AI 统一调度）            │    │
│  └─────────────────────────────────────────────────┘    │
│              ↓                        ↓                  │
│  ┌───────────────┐       ┌────────────────────────┐     │
│  │  MySQL :3306  │       │ SiliconFlow API（外网）│     │
│  │    lexai_db   │       │  腾讯混元 a13b 模型    │     │
│  └───────────────┘       └────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

### 技术栈

| 层级 | 技术选型 |
|------|----------|
| **前端框架** | Vue 3.4 + TypeScript 6.0 + Vite 5.0 |
| **前端状态** | Pinia 2.1（JWT 认证状态管理） |
| **前端路由** | Vue Router 4.2（路由守卫） |
| **HTTP 客户端** | Axios 1.6（统一拦截器，自动注入 JWT） |
| **后端框架** | Spring Boot 3.2 + Java 17 |
| **安全框架** | Spring Security + JWT（jjwt 0.12.3） |
| **持久层** | Spring Data JPA + MySQL 8.0 |
| **AI 接入** | SiliconFlow API（腾讯混元 a13b-instruct） |
| **文档解析** | Apache Tika 2.9.2 |
| **API 文档** | SpringDoc OpenAPI 2.3.0（Swagger UI） |

---

## 快速开始

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

### 4. 访问服务

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:3000 |
| 后端 API | http://localhost:8089 |
| Swagger 文档 | http://localhost:8089/swagger-ui.html |

> 首次使用请访问 http://localhost:3000/register 注册账号。

---

## 项目结构

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
│       │   └── AiService              # AI 调度中心（统一封装 SiliconFlow 调用）
│       ├── repository/               # JPA 数据访问层
│       ├── entity/                   # 实体类
│       ├── dto/                      # 数据传输对象
│       ├── security/                 # JWT 认证
│       └── common/                   # 通用响应封装
│
├── frontend/                         # Vue 3 前端
│   └── src/
│       ├── views/                    # 页面组件
│       ├── components/              # 公共组件
│       ├── stores/                   # Pinia 状态
│       ├── router/                  # 路由配置
│       └── api/                     # Axios 封装
│
└── database/
    └── schema.sql                    # 数据库建表脚本
```

---

## AI 能力

AiService 作为系统的 AI 调度中心，统一封装 SiliconFlow API 调用，覆盖以下核心能力：

| 合同类型 | 基础审查 | 高级审查 |
|----------|---------|---------|
| 劳动合同 | ✓ | ✓ |
| 租赁合同 | ✓ | ✓ |
| 买卖合同 | ✓ | ✓ |
| 借款合同 | ✓ | ✓ |
| 服务合同 | ✓ | ✓ |
| 技术合同 | ✓ | ✓ |
| 投资合同 | ✓ | ✓ |

---

## 配置说明

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

## 常见问题

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

系统没有预设账号，请访问 http://localhost:3000/register 注册第一个账号。
</details>

<details>
<summary><strong>前端修改后需要重启吗？</strong></summary>

不需要。Vite 开发服务器支持热模块替换（Hot Module Replacement），修改代码后浏览器会自动刷新。
</details>

---

## License

本项目采用 [MIT License](LICENSE) 开源。

Copyright © 2026 LexAI.
