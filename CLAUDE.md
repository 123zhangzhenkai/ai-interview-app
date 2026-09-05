# CLAUDE.md

本文件为 Claude Code 在本仓库工作时的开发规范与约定。所有代码、提交、接口实现必须遵循本文档。

## 1. 项目简介

**offerAI 智能面试官** —— 一款 AI 面试辅导产品，基于 [.cursor/PRD.md](.cursor/PRD.md) 需求文档。

核心能力：

- **登录注册**：账号密码 / 手机验证码 / 微信 / QQ 快捷登录，新用户 1 分钟引导
- **信息登记**：求职档案（个人 / 教育 / 实习工作 / 技能证书 / 求职偏好 / 补充信息），AI 一键生成自我介绍
- **模拟面试**：1 对 1 / 1 对多群面，AI 面试官实时问答、追问、评分、改进建议（基于 Dify 工作流）
- **简历优化**：上传 PDF/Word，AI 解析并给出排版 / 表达 / 亮点 / 匹配度建议
- **就业指导**：心理疏导、AI 情感陪伴、正能量内容推荐

> 技术关键点：AI 面试官逻辑与简历解析均通过 **Dify 工作流** 实现，后端主要负责编排与数据落库。

---

## 2. 技术栈

| 层 | 选型 | 说明 |
|----|------|------|
| 前端 | React 18 + TypeScript + Vite | 响应式 H5，移动端优先 |
| UI 组件 | Ant Design 5 | 中后台与表单类界面 |
| 样式 | Tailwind CSS | 布局与细节样式，与 AntD 配合 |
| 前端状态 | Zustand + TanStack Query | 全局状态 / 服务端状态 |
| 后端 | Python 3.11 + FastAPI | 异步接口，编排 Dify 与业务 |
| 数据校验 | Pydantic v2 | 请求/响应模型 |
| ORM | SQLAlchemy 2.0 (async) + Alembic | 数据访问与迁移 |
| 数据库 | PostgreSQL 16 | 主存储 |
| 缓存 / 会话 | Redis 7 | 验证码、会话、限流、热点缓存 |
| 对象存储 | MinIO（本地）/ 阿里云 OSS（生产） | 简历文件、音视频 |
| AI 编排 | Dify（工作流） | 面试官逻辑、简历解析、自我介绍、润色 |
| 语音 | ASR（语音转文字）+ TTS | 对接第三方语音服务 |
| 部署 | Docker + Docker Compose + Nginx | 容器化部署 |

### 依赖约束

- **后端不直接硬编码大模型 Prompt**：所有 AI 逻辑在 Dify 工作流中维护，后端通过 Dify API 调用，仅传业务参数与上下文。
- **语音与视频为渐进能力**：MVP 阶段文字对话优先，ASR/TTS/视频接口需抽象，便于后续接入。

---

## 3. 目录结构

```
zhang/
├── CLAUDE.md
├── .cursor/
│   └── PRD.md                # 产品需求文档（唯一事实来源）
├── frontend/                 # React 前端
│   ├── src/
│   │   ├── api/              # 接口封装（与后端一一对应）
│   │   ├── components/       # 通用组件
│   │   ├── pages/            # 页面
│   │   ├── store/            # Zustand 状态
│   │   ├── hooks/            # 自定义 hooks
│   │   ├── types/            # TS 类型定义
│   │   └── utils/            # 工具函数
│   └── ...
├── backend/                  # FastAPI 后端
│   ├── app/
│   │   ├── api/              # 路由层（接口）
│   │   ├── core/             # 配置、安全、依赖
│   │   ├── models/           # SQLAlchemy 模型
│   │   ├── schemas/          # Pydantic 模型
│   │   ├── services/         # 业务逻辑（含 Dify 编排）
│   │   ├── crud/             # 数据访问
│   │   └── main.py           # 入口
│   ├── alembic/              # 数据库迁移
│   └── tests/                # 测试
├── deploy/                   # Docker / Nginx 配置
└── docs/                     # 补充文档
```

---

## 4. 开发环境与命令

```bash
# 前端
cd frontend
pnpm install        # 依赖安装（统一使用 pnpm）
pnpm dev            # 本地开发
pnpm build          # 构建
pnpm lint           # ESLint + 类型检查

# 后端
cd backend
poetry install      # 依赖安装（统一使用 Poetry）
poetry run uvicorn app.main:app --reload   # 本地开发
poetry run alembic upgrade head            # 数据库迁移
poetry run pytest                          # 测试
```

- 环境变量统一通过 `.env` 管理，示例见 `.env.example`，**严禁提交真实密钥**。
- 本地依赖：PostgreSQL、Redis、MinIO、Dify 均通过 `deploy/docker-compose.yml` 一键启动。

---

## 5. 代码规范

### 5.1 通用

- 所有注释、commit message、文档用 **中文**；标识符、代码、技术名词用英文。
- 禁止提交：`node_modules/`、`.env`、`__pycache__/`、`dist/`、`.DS_Store`，已在 `.gitignore` 排除。
- 每个 PR 保持单一职责，改动聚焦一个功能点。
- 不得包含 `TODO`/`FIXME` 未处理标记直接进入主干。

### 5.2 前端（TypeScript / React）

- 开启 **TypeScript strict 模式**，禁止 `any`（确有需要需注释说明并评审）。
- 组件：函数组件 + Hooks；优先函数式风格，禁用 class 组件。
- 命名：组件 `PascalCase`，函数/变量 `camelCase`，常量 `UPPER_SNAKE_CASE`，类型/接口 `PascalCase`。
- 状态分层：
  - 服务端数据用 **TanStack Query**，禁止在组件内手动 `fetch` + `useEffect` 重复请求。
  - 跨页全局 UI 状态用 **Zustand**，避免过度全局化。
- 样式优先 Tailwind 原子类，页面级布局可与 AntD 组件搭配；避免内联样式。
- 表单统一使用 AntD Form + 校验规则。
- 路由、请求、错误处理需统一封装，接口层集中在 `src/api/`，禁止在组件内散落请求逻辑。
- 代码格式化：Prettier；质量检查：ESLint（含 `@typescript-eslint`）。

### 5.3 后端（Python / FastAPI）

- Python 3.11，所有函数必须带**类型注解**；使用 `ruff`（lint + format）与 `mypy` 检查。
- 命名：类 `PascalCase`，函数/变量 `snake_case`，常量 `UPPER_SNAKE_CASE`。
- 分层职责：
  - `api/` 只做参数校验与响应返回，不写业务逻辑。
  - `services/` 承载业务编排（含 Dify 调用），可复用。
  - `crud/` 只做数据库读写。
- 数据库访问用 **async SQLAlchemy**，禁止在请求处理中直接写裸 SQL 字符串。
- 所有请求/响应模型用 Pydantic v2 定义，统一返回结构：`{ code, message, data }`。
- 错误处理统一走全局异常处理器，接口内不散落 try/except 吞异常。
- 敏感配置（数据库、Dify、第三方密钥）从 `core/config.py` 通过 Pydantic Settings 读取。

### 5.4 Git 提交规范（Conventional Commits）

```
<type>(<scope>): <subject>
```

| type | 含义 |
|------|------|
| feat | 新功能 |
| fix | 修复 |
| refactor | 重构 |
| docs | 文档 |
| style | 格式（不影响逻辑） |
| test | 测试 |
| chore | 构建/工具/依赖 |

示例：`feat(interview): 新增 1 对多群面模拟接口`、`fix(resume): 修复 PDF 解析超时问题`。

---

## 6. 开发要求（关键约定）

### 6.1 AI / Dify 集成规范

- **Prompt 与工作流在 Dify 侧维护**，后端仅通过 API 传入结构化参数，不内嵌业务 Prompt。
- 后端封装统一的 Dify 客户端（`services/dify_client.py`），统一处理：超时、重试、流式返回、错误降级。
- AI 返回结果必须**结构化**（JSON），经 Pydantic 校验后再落库，避免把非结构化文本直接写入数据库。
- 涉及用户隐私数据（简历、面试回答）传给 Dify 时，需脱敏处理并在日志中屏蔽明文。

### 6.2 接口规范

- RESTful 风格，前缀 `/api/v1/`，路径用复数名词（如 `/api/v1/interviews`）。
- 认证：JWT（Bearer Token），登录接口返回 access/refresh token。
- 面试对话建议使用 **SSE 流式返回**，保证答题评分与追问的实时体验。
- 统一响应结构：`{ "code": 0, "message": "ok", "data": {...} }`，`code != 0` 表示业务异常。

### 6.3 数据与隐私要求（强制）

本项目处理简历、面试回答等**敏感个人信息**，须遵守《个人信息保护法》《数据安全法》：

- 简历、面试记录等敏感数据：**传输加密（TLS）、存储加密**。
- 用户上传简历文件仅存储于对象存储私有桶，禁止公开读。
- 日志中禁止输出：手机号、邮箱、简历内容、面试回答原文（可输出脱敏后的摘要）。
- 支持账号注销，注销后按约定周期删除个人数据。
- 新增任何涉及个人数据的字段或接口，必须同步更新隐私说明。

### 6.4 模块与 PRD 的对应关系

| 前端模块 | 后端模块 | PRD 章节 |
|----------|----------|----------|
| 登录/注册 | `auth` | 一、首页与登录模块 |
| 求职档案 / 自我介绍 | `profile` | 二、信息登记模块 |
| 模拟面试 | `interview` | 三、模拟面试模块 |
| 简历优化 | `resume` | 四、简历优化模块 |
| 就业指导 | `guidance` | 五、就业指导模块 |

> 需求变更先改 [.cursor/PRD.md](.cursor/PRD.md)，再同步本文件与代码；以 PRD 为唯一事实来源。

### 6.5 质量门槛

- 新功能必须附带测试：后端单测覆盖核心 service；前端关键流程补充组件测试。
- 提交前确保：`pnpm lint` 与 `poetry run ruff check`、`poetry run mypy` 全部通过。
- 涉及数据库结构变更，必须提供 Alembic 迁移脚本。

---

## 7. 技术决策说明（可调整项）

以下为本文档确立的默认选型，如需调整请更新本文档并同步团队：

1. 前端为**响应式 H5 Web 应用**（移动端优先），暂不做原生 App / 小程序；后续如需小程序再评估跨端方案。
2. 后端选用 **Python + FastAPI**（而非 Node），因其与 AI/Dify 生态契合、类型校验完善。
3. MVP 阶段对话以**文字为主**，语音（ASR/TTS）与视频面试作为 P1 能力预留接口。
