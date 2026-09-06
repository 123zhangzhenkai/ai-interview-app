# offerAI 智能面试官 · 后端

基于 **FastAPI + SQLAlchemy 2.0 (async) + aiomysql + MySQL 8.0 + Alembic** 的后端骨架，遵循 [CLAUDE.md](../CLAUDE.md) 分层规范，数据表与 [db.md](../db.md) 一一对应。

## 目录结构

```
backend/
├── app/
│   ├── api/v1/        # 路由层：参数校验与响应返回（auth/profile/interview/resume/guidance）
│   ├── core/          # 配置、数据库、安全、依赖、异常处理
│   ├── models/        # SQLAlchemy 模型（26 张表）
│   ├── schemas/       # Pydantic 模型
│   ├── services/      # 业务逻辑（auth、dify_client）
│   ├── crud/          # 数据访问
│   └── main.py        # 入口
├── alembic/           # 数据库迁移
├── tests/             # 测试
├── pyproject.toml
└── .env.example
```

## 初始化与运行命令

```bash
cd backend

# 1. 安装依赖（Poetry）
poetry install

# 2. 准备环境变量
cp .env.example .env    # 编辑 .env 填入真实 MySQL/Dify 密钥

# 3. 创建数据库（首次，需本地已启动 MySQL 8.0）
mysql -uroot -p -e "CREATE DATABASE IF NOT EXISTS offer_ai DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 4. 初始化 Alembic（已内置，仅首次手动 init 时才需要；本项目已配置好，无需再执行）
# poetry run alembic init alembic

# 5. 自动生成迁移脚本（根据 models 与库结构差异）
poetry run alembic revision --autogenerate -m "init tables"

# 6. 应用迁移到数据库
poetry run alembic upgrade head

# 7. 启动服务
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 常用命令

```bash
poetry run alembic history            # 查看迁移历史
poetry run alembic downgrade -1       # 回滚一个版本
poetry run alembic upgrade +1         # 前进一个版本
poetry run pytest                     # 运行测试
poetry run ruff check .               # 代码检查
poetry run mypy app                   # 类型检查
```

## 接口一览（前缀 /api/v1）

| 模块 | 方法与路径 | 说明 |
|------|-----------|------|
| 健康检查 | GET `/health` | 应用健康 |
| 认证 | POST `/auth/register` | 注册 |
| 认证 | POST `/auth/login` | 登录 |
| 认证 | POST `/auth/refresh` | 刷新令牌 |
| 档案 | GET/PUT `/profiles/me` | 获取/更新当前用户档案 |
| 面试 | GET/POST `/interviews`、GET `/interviews/{id}` | 面试会话 |
| 简历 | GET/POST `/resumes` | 简历记录 |
| 指导 | GET/POST `/guidance/chats` | 陪伴会话 |

## 说明

1. **统一响应**：所有接口返回 `{ code, message, data }`；`code == 0` 成功，业务异常 `code != 0`（HTTP 200），协议级错误（401/404/422/500）由全局异常处理器兜底。
2. **认证**：JWT Bearer Token，`access_token` 30 分钟 / `refresh_token` 7 天。
3. **数据库**：`aiomysql` 异步驱动；连接串由 `core/config.py` 从 `.env` 读取。
4. **类型映射**：ORM 使用可移植类型（`Boolean`→TINYINT(1)、`BigInteger`→BIGINT、`Numeric`→DECIMAL），权威 DDL 以 db.md 为准；`alembic autogenerate` 生成的 MySQL DDL 与之等价（`unsigned` 属性略去不影响业务）。
5. **Dify 集成**：`services/dify_client.py` 封装超时/重试/流式，业务 Prompt 全部在 Dify 侧维护，后端仅传结构化参数。
