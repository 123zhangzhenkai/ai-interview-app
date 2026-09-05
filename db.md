# db.md — offerAI 智能面试官 · 数据库设计文档

> 基于 [.cursor/PRD.md](.cursor/PRD.md) 与 [DESIGN.md](DESIGN.md) 编写。
> 本文档给出全部数据表的字段设计（字段名 / 类型 / 主键 / 非空 / 注释），文末附**可直接运行的 MySQL 8.0 建表语句**。
>
> ✅ 版本说明：本项目统一采用 **MySQL 8.0**（与 CLAUDE.md 技术栈一致）。本文档建表语句可直接在 MySQL 8.0+ 上运行。

---

## 0. 设计约定

| 项 | 约定 |
|----|------|
| 数据库 | `offer_ai`，字符集 `utf8mb4`，排序规则 `utf8mb4_unicode_ci` |
| 引擎 | InnoDB |
| 命名 | 表名/字段名 `snake_case`，表名复数 |
| 主键 | 统一 `id BIGINT UNSIGNED AUTO_INCREMENT` |
| 通用字段 | 每表带 `created_at`（创建时间）、`updated_at`（更新时间） |
| 逻辑外键 | **只建索引，不建物理外键约束**（便于分库分表与迁移，完整性由应用层保证） |
| 布尔 | `TINYINT(1)`，0/1 |
| 状态枚举 | `VARCHAR` + 注释列举取值（可读性强、便于扩展） |
| 金额 | `DECIMAL(10,2)` |
| 分数 | `DECIMAL(4,1)`（单题/维度）、`DECIMAL(5,2)`（总分） |

---

## 1. 表清单总览

| 模块 | 表名 | 说明 | 优先级 |
|------|------|------|--------|
| 账号认证 | `users` | 用户账号表 | P0 |
| 账号认证 | `third_party_accounts` | 第三方登录绑定表 | P0 |
| 账号认证 | `verification_codes` | 短信验证码表 | P0 |
| 求职档案 | `profiles` | 基础个人信息表 | P0 |
| 求职档案 | `educations` | 教育经历表 | P0 |
| 求职档案 | `work_experiences` | 实习/工作经历表 | P0 |
| 求职档案 | `user_skills` | 技能表 | P0 |
| 求职档案 | `user_certificates` | 证书表 | P0 |
| 求职档案 | `job_preferences` | 求职偏好表 | P0 |
| 求职档案 | `profile_extras` | 补充信息表 | P0 |
| 求职档案 | `self_introductions` | 智能自我介绍表 | P0 |
| 模拟面试 | `interviews` | 面试会话表 | P0 |
| 模拟面试 | `interview_messages` | 面试对话记录表 | P0 |
| 模拟面试 | `interview_feedbacks` | 面试逐题点评表 | P0 |
| 模拟面试 | `interview_reports` | 面试报告表 | P0 |
| 简历优化 | `resumes` | 简历表 | P0 |
| 简历优化 | `resume_analyses` | 简历分析结果表 | P0 |
| 简历优化 | `resume_suggestions` | 简历优化建议表 | P0 |
| 就业指导 | `guidance_chats` | 就业指导会话表 | P1 |
| 就业指导 | `guidance_messages` | 陪伴/指导消息表 | P1 |
| 就业指导 | `guidance_contents` | 就业指导内容表 | P1 |
| 商业化 | `memberships` | 会员表 | P1 |
| 商业化 | `orders` | 订单表 | P1 |
| 后期规划 | `real_interviews` | 真人模拟面试预约表 | P2 |
| 后期规划 | `wall_questions` | 真人问答墙问题表 | P2 |
| 后期规划 | `wall_answers` | 真人问答墙回答表 | P2 |

---

## 2. 逐表详细设计

### 2.1 users（用户账号表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 用户ID |
| phone | VARCHAR(20) | | | 手机号（第三方登录可为空） |
| password_hash | VARCHAR(255) | | | 密码哈希（第三方登录为空） |
| nickname | VARCHAR(50) | | | 昵称 |
| avatar_url | VARCHAR(255) | | | 头像URL |
| status | TINYINT | | ✅ | 账号状态：0禁用 1正常 |
| last_login_at | DATETIME | | | 最后登录时间 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`uk_phone`(phone 唯一)

### 2.2 third_party_accounts（第三方登录绑定表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 绑定ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| provider | VARCHAR(20) | | ✅ | 平台：wechat / qq |
| open_id | VARCHAR(128) | | ✅ | 第三方OpenID |
| union_id | VARCHAR(128) | | | 微信UnionID |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`uk_provider_open`(provider, open_id 唯一)、`idx_user`(user_id)

### 2.3 verification_codes（短信验证码表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 记录ID |
| phone | VARCHAR(20) | | ✅ | 手机号 |
| code | VARCHAR(10) | | ✅ | 验证码 |
| scene | VARCHAR(20) | | ✅ | 场景：login / register / reset_password |
| expires_at | DATETIME | | ✅ | 过期时间 |
| is_used | TINYINT(1) | | ✅ | 是否已使用：0否 1是 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_phone_scene`(phone, scene)

### 2.4 profiles（基础个人信息表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 档案ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID（一对一） |
| real_name | VARCHAR(50) | | | 姓名 |
| gender | TINYINT | | | 性别：0未知 1男 2女 |
| age | TINYINT UNSIGNED | | | 年龄 |
| phone | VARCHAR(20) | | | 联系电话 |
| email | VARCHAR(100) | | | 常用邮箱 |
| target_position | VARCHAR(100) | | | 意向岗位 |
| target_city | VARCHAR(50) | | | 期望工作城市 |
| expected_salary_min | DECIMAL(10,2) | | | 期望薪资下限 |
| expected_salary_max | DECIMAL(10,2) | | | 期望薪资上限 |
| available_date | VARCHAR(50) | | | 可到岗时间 |
| job_seeker_type | VARCHAR(20) | | | 求职身份：fresh / graduate / career_change / employed |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`uk_user`(user_id 唯一)

### 2.5 educations（教育经历表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 经历ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| degree | VARCHAR(20) | | | 最高学历 |
| school | VARCHAR(100) | | | 毕业院校 |
| major | VARCHAR(100) | | | 专业 |
| start_date | DATE | | | 入学时间 |
| end_date | DATE | | | 毕业时间 |
| main_courses | TEXT | | | 主修核心课程 |
| honors | TEXT | | | 荣誉/奖学金（选填） |
| gpa | VARCHAR(20) | | | 学业成绩（选填） |
| campus_projects | TEXT | | | 校园项目/竞赛/社团 |
| sort_order | INT | | ✅ | 排序 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`idx_user`(user_id)

### 2.6 work_experiences（实习/工作经历表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 经历ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| company_name | VARCHAR(100) | | | 公司名称 |
| position | VARCHAR(100) | | | 岗位名称 |
| start_date | DATE | | | 入职时间 |
| end_date | DATE | | | 离职时间 |
| job_content | TEXT | | | 工作内容 |
| responsible_area | TEXT | | | 负责板块 |
| skills | TEXT | | | 实操技能 |
| tools | TEXT | | | 常用工具 |
| achievements | TEXT | | | 工作成果/业绩/项目案例 |
| leave_reason | TEXT | | | 离职原因（选填，供AI追问） |
| sort_order | INT | | ✅ | 排序 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`idx_user`(user_id)

### 2.7 user_skills（技能表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 技能ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| skill_name | VARCHAR(50) | | ✅ | 技能名称 |
| skill_type | VARCHAR(20) | | ✅ | 类型：professional / office / language |
| level | VARCHAR(20) | | | 熟练程度 |
| sort_order | INT | | ✅ | 排序 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_user`(user_id)

### 2.8 user_certificates（证书表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 证书ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| cert_name | VARCHAR(100) | | ✅ | 证书名称 |
| cert_type | VARCHAR(20) | | | 类型：vocational / english / computer |
| issue_date | DATE | | | 获取时间 |
| sort_order | INT | | ✅ | 排序 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_user`(user_id)

### 2.9 job_preferences（求职偏好表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 偏好ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID（一对一） |
| target_industry | VARCHAR(100) | | | 意向行业 |
| company_type | VARCHAR(50) | | | 企业类型 |
| accept_overtime | TINYINT(1) | | | 是否接受加班 |
| accept_business_trip | TINYINT(1) | | | 是否接受出差 |
| accept_relocation | TINYINT(1) | | | 是否接受异地工作 |
| interview_round_pref | VARCHAR(50) | | | 面试轮次偏好：hr / tech / final |
| interview_style | VARCHAR(20) | | | 面试风格：formal / casual |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`uk_user`(user_id 唯一)

### 2.10 profile_extras（补充信息表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 记录ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID（一对一） |
| self_assessment | TEXT | | | 个人优缺点自评 |
| career_plan | TEXT | | | 职业规划与发展方向 |
| hobbies | TEXT | | | 兴趣爱好 |
| specialties | TEXT | | | 个人特长 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`uk_user`(user_id 唯一)

### 2.11 self_introductions（智能自我介绍表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 记录ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| duration_type | VARCHAR(20) | | ✅ | 时长：1min / 3min |
| scenario | VARCHAR(20) | | ✅ | 场景：campus / social / career_change / english |
| content | TEXT | | | 自我介绍内容 |
| is_ai_generated | TINYINT(1) | | ✅ | 是否AI生成：0否 1是 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`idx_user`(user_id)

### 2.12 interviews（面试会话表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 面试ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| interview_mode | VARCHAR(20) | | ✅ | 模式：one_to_one / group |
| target_position | VARCHAR(100) | | | 面试岗位 |
| interview_round | VARCHAR(20) | | | 轮次：hr / tech / final |
| interview_style | VARCHAR(20) | | | 风格：formal / casual |
| status | VARCHAR(20) | | ✅ | 状态：ongoing / finished / cancelled |
| total_questions | INT | | ✅ | 题目总数 |
| current_question | INT | | ✅ | 当前题号 |
| total_score | DECIMAL(5,2) | | | 总分 |
| started_at | DATETIME | | | 开始时间 |
| finished_at | DATETIME | | | 结束时间 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`idx_user`(user_id)、`idx_user_status`(user_id, status)

### 2.13 interview_messages（面试对话记录表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 消息ID |
| interview_id | BIGINT UNSIGNED | | ✅ | 面试ID |
| role | VARCHAR(10) | | ✅ | 角色：ai / user |
| interviewer_name | VARCHAR(50) | | | 面试官标识（群面：A/B/C） |
| question_index | INT | | | 所属题号 |
| message_type | VARCHAR(20) | | | 类型：question / answer / followup / score |
| content | TEXT | | | 内容 |
| asr_text | TEXT | | | 语音转文字原文 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_interview`(interview_id)

### 2.14 interview_feedbacks（面试逐题点评表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 点评ID |
| interview_id | BIGINT UNSIGNED | | ✅ | 面试ID |
| question_index | INT | | ✅ | 题号 |
| question_text | TEXT | | | 题目内容 |
| user_answer_summary | TEXT | | | 用户回答摘要 |
| total_score | DECIMAL(4,1) | | | 本题总分 |
| content_score | DECIMAL(4,1) | | | 内容质量分 |
| logic_score | DECIMAL(4,1) | | | 逻辑结构分 |
| expression_score | DECIMAL(4,1) | | | 表达沟通分 |
| professional_score | DECIMAL(4,1) | | | 专业匹配分 |
| highlights | TEXT | | | 亮点 |
| issues | TEXT | | | 主要问题 |
| suggestions | TEXT | | | 改进建议 |
| sample_answer | TEXT | | | 示范回答 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_interview`(interview_id)

### 2.15 interview_reports（面试报告表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 报告ID |
| interview_id | BIGINT UNSIGNED | | ✅ | 面试ID（一对一） |
| total_score | DECIMAL(5,2) | | | 总分 |
| overall_comment | TEXT | | | 整体评价 |
| core_suggestions | TEXT | | | 3条核心改进建议 |
| next_practice_suggestions | TEXT | | | 下次练习建议 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`uk_interview`(interview_id 唯一)

### 2.16 resumes（简历表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 简历ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| file_name | VARCHAR(255) | | ✅ | 文件名 |
| file_url | VARCHAR(255) | | | 对象存储URL |
| file_type | VARCHAR(10) | | | 类型：pdf / word |
| file_size | BIGINT | | | 文件大小（字节） |
| upload_status | VARCHAR(20) | | ✅ | 上传状态：uploading / uploaded / failed |
| parse_status | VARCHAR(20) | | ✅ | 解析状态：pending / parsing / done / failed |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`idx_user`(user_id)

### 2.17 resume_analyses（简历分析结果表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 分析ID |
| resume_id | BIGINT UNSIGNED | | ✅ | 简历ID（一对一） |
| total_score | DECIMAL(4,1) | | | 综合评分 |
| layout_score | DECIMAL(4,1) | | | 排版分 |
| expression_score | DECIMAL(4,1) | | | 表达分 |
| highlight_score | DECIMAL(4,1) | | | 亮点分 |
| match_score | DECIMAL(4,1) | | | 匹配度分 |
| optimized_content | TEXT | | | 优化版简历内容 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`uk_resume`(resume_id 唯一)

### 2.18 resume_suggestions（简历优化建议表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 建议ID |
| analysis_id | BIGINT UNSIGNED | | ✅ | 分析ID |
| category | VARCHAR(20) | | ✅ | 分类：layout / expression / highlight / match |
| title | VARCHAR(255) | | | 建议标题 |
| description | TEXT | | | 建议内容 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_analysis`(analysis_id)

### 2.19 guidance_chats（就业指导会话表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 会话ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| chat_type | VARCHAR(20) | | ✅ | 类型：companion / other |
| status | VARCHAR(20) | | ✅ | 状态：ongoing / finished |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`idx_user`(user_id)

### 2.20 guidance_messages（陪伴/指导消息表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 消息ID |
| chat_id | BIGINT UNSIGNED | | ✅ | 会话ID |
| role | VARCHAR(10) | | ✅ | 角色：ai / user |
| content | TEXT | | | 内容 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_chat`(chat_id)

### 2.21 guidance_contents（就业指导内容表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 内容ID |
| title | VARCHAR(255) | | ✅ | 标题 |
| content_type | VARCHAR(20) | | ✅ | 类型：article / music / video |
| category | VARCHAR(20) | | ✅ | 分类：psychology / positive / skill |
| cover_url | VARCHAR(255) | | | 封面图URL |
| content_url | VARCHAR(255) | | | 内容地址 |
| status | TINYINT | | ✅ | 上架状态：0下架 1上架 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`idx_category_status`(category, status)

### 2.22 memberships（会员表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 会员ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID（一对一） |
| plan_type | VARCHAR(20) | | ✅ | 套餐：free / vip |
| start_date | DATETIME | | | 生效时间 |
| end_date | DATETIME | | | 到期时间 |
| status | TINYINT | | ✅ | 状态：0失效 1生效 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`uk_user`(user_id 唯一)

### 2.23 orders（订单表）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 订单ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| order_no | VARCHAR(64) | | ✅ | 订单号 |
| plan_type | VARCHAR(20) | | ✅ | 套餐类型 |
| amount | DECIMAL(10,2) | | ✅ | 金额（元） |
| pay_status | TINYINT | | ✅ | 支付状态：0待支付 1已支付 2已取消 |
| pay_channel | VARCHAR(20) | | | 支付渠道：wechat / alipay |
| paid_at | DATETIME | | | 支付时间 |
| created_at | DATETIME | | ✅ | 创建时间 |
| updated_at | DATETIME | | ✅ | 更新时间 |

索引：`uk_order_no`(order_no 唯一)、`idx_user`(user_id)

### 2.24 real_interviews（真人模拟面试预约表 · P2）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 预约ID |
| user_id | BIGINT UNSIGNED | | ✅ | 用户ID |
| interviewer_id | BIGINT UNSIGNED | | | 真人面试官ID |
| scheduled_at | DATETIME | | | 预约时间 |
| status | VARCHAR(20) | | ✅ | 状态：pending / confirmed / cancelled / finished |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_user`(user_id)

### 2.25 wall_questions（真人问答墙问题表 · P2）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 问题ID |
| user_id | BIGINT UNSIGNED | | ✅ | 提问用户ID |
| title | VARCHAR(255) | | ✅ | 问题标题 |
| content | TEXT | | | 问题详情 |
| view_count | INT | | ✅ | 浏览数 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_user`(user_id)

### 2.26 wall_answers（真人问答墙回答表 · P2）

| 字段 | 类型 | 主键 | 非空 | 注释 |
|------|------|:----:|:----:|------|
| id | BIGINT UNSIGNED | ✅ | ✅ | 回答ID |
| question_id | BIGINT UNSIGNED | | ✅ | 问题ID |
| answerer_id | BIGINT UNSIGNED | | | 回答者ID |
| content | TEXT | | | 回答内容 |
| created_at | DATETIME | | ✅ | 创建时间 |

索引：`idx_question`(question_id)

---

## 3. 实体关系（ER）简述

```
users 1─┬─1 profiles / job_preferences / profile_extras / memberships
        ├─N educations / work_experiences / user_skills / user_certificates
        ├─N self_introductions
        ├─N interviews ─N interview_messages / interview_feedbacks
        │              └1 interview_reports
        ├─N resumes ─1 resume_analyses ─N resume_suggestions
        ├─N guidance_chats ─N guidance_messages
        ├─N orders
        ├─N third_party_accounts
        └─N real_interviews / wall_questions / wall_answers
```

---

## 4. 可直接运行的 MySQL 建表语句

```sql
-- =============================================================
-- offerAI 智能面试官 数据库初始化脚本
-- MySQL 8.0+ · utf8mb4
-- =============================================================
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS `offer_ai`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE `offer_ai`;

-- ---------- 账号认证 ----------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `phone`         VARCHAR(20)  DEFAULT NULL COMMENT '手机号（第三方登录可为空）',
  `password_hash` VARCHAR(255) DEFAULT NULL COMMENT '密码哈希（第三方登录为空）',
  `nickname`      VARCHAR(50)  DEFAULT NULL COMMENT '昵称',
  `avatar_url`    VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
  `status`        TINYINT      NOT NULL DEFAULT 1 COMMENT '账号状态：0禁用 1正常',
  `last_login_at` DATETIME     DEFAULT NULL COMMENT '最后登录时间',
  `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户账号表';

DROP TABLE IF EXISTS `third_party_accounts`;
CREATE TABLE `third_party_accounts` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '绑定ID',
  `user_id`    BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `provider`   VARCHAR(20)  NOT NULL COMMENT '平台：wechat / qq',
  `open_id`    VARCHAR(128) NOT NULL COMMENT '第三方OpenID',
  `union_id`   VARCHAR(128) DEFAULT NULL COMMENT '微信UnionID',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_provider_open` (`provider`, `open_id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='第三方登录绑定表';

DROP TABLE IF EXISTS `verification_codes`;
CREATE TABLE `verification_codes` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `phone`      VARCHAR(20) NOT NULL COMMENT '手机号',
  `code`       VARCHAR(10) NOT NULL COMMENT '验证码',
  `scene`      VARCHAR(20) NOT NULL COMMENT '场景：login / register / reset_password',
  `expires_at` DATETIME    NOT NULL COMMENT '过期时间',
  `is_used`    TINYINT(1)  NOT NULL DEFAULT 0 COMMENT '是否已使用：0否 1是',
  `created_at` DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_phone_scene` (`phone`, `scene`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='短信验证码表';

-- ---------- 求职档案 ----------
DROP TABLE IF EXISTS `profiles`;
CREATE TABLE `profiles` (
  `id`                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '档案ID',
  `user_id`            BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `real_name`          VARCHAR(50)  DEFAULT NULL COMMENT '姓名',
  `gender`             TINYINT      DEFAULT NULL COMMENT '性别：0未知 1男 2女',
  `age`                TINYINT UNSIGNED DEFAULT NULL COMMENT '年龄',
  `phone`              VARCHAR(20)  DEFAULT NULL COMMENT '联系电话',
  `email`              VARCHAR(100) DEFAULT NULL COMMENT '常用邮箱',
  `target_position`    VARCHAR(100) DEFAULT NULL COMMENT '意向岗位',
  `target_city`        VARCHAR(50)  DEFAULT NULL COMMENT '期望工作城市',
  `expected_salary_min` DECIMAL(10,2) DEFAULT NULL COMMENT '期望薪资下限',
  `expected_salary_max` DECIMAL(10,2) DEFAULT NULL COMMENT '期望薪资上限',
  `available_date`     VARCHAR(50)  DEFAULT NULL COMMENT '可到岗时间',
  `job_seeker_type`    VARCHAR(20)  DEFAULT NULL COMMENT '求职身份：fresh / graduate / career_change / employed',
  `created_at`         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='基础个人信息表';

DROP TABLE IF EXISTS `educations`;
CREATE TABLE `educations` (
  `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '经历ID',
  `user_id`         BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `degree`          VARCHAR(20)  DEFAULT NULL COMMENT '最高学历',
  `school`          VARCHAR(100) DEFAULT NULL COMMENT '毕业院校',
  `major`           VARCHAR(100) DEFAULT NULL COMMENT '专业',
  `start_date`      DATE         DEFAULT NULL COMMENT '入学时间',
  `end_date`        DATE         DEFAULT NULL COMMENT '毕业时间',
  `main_courses`    TEXT         COMMENT '主修核心课程',
  `honors`          TEXT         COMMENT '荣誉/奖学金',
  `gpa`             VARCHAR(20)  DEFAULT NULL COMMENT '学业成绩',
  `campus_projects` TEXT         COMMENT '校园项目/竞赛/社团',
  `sort_order`      INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='教育经历表';

DROP TABLE IF EXISTS `work_experiences`;
CREATE TABLE `work_experiences` (
  `id`               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '经历ID',
  `user_id`          BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `company_name`     VARCHAR(100) DEFAULT NULL COMMENT '公司名称',
  `position`         VARCHAR(100) DEFAULT NULL COMMENT '岗位名称',
  `start_date`       DATE         DEFAULT NULL COMMENT '入职时间',
  `end_date`         DATE         DEFAULT NULL COMMENT '离职时间',
  `job_content`      TEXT COMMENT '工作内容',
  `responsible_area` TEXT COMMENT '负责板块',
  `skills`           TEXT COMMENT '实操技能',
  `tools`            TEXT COMMENT '常用工具',
  `achievements`     TEXT COMMENT '工作成果/业绩/项目案例',
  `leave_reason`     TEXT COMMENT '离职原因（选填，供AI追问）',
  `sort_order`       INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='实习/工作经历表';

DROP TABLE IF EXISTS `user_skills`;
CREATE TABLE `user_skills` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '技能ID',
  `user_id`    BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `skill_name` VARCHAR(50) NOT NULL COMMENT '技能名称',
  `skill_type` VARCHAR(20) NOT NULL COMMENT '类型：professional / office / language',
  `level`      VARCHAR(20) DEFAULT NULL COMMENT '熟练程度',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='技能表';

DROP TABLE IF EXISTS `user_certificates`;
CREATE TABLE `user_certificates` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '证书ID',
  `user_id`    BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `cert_name`  VARCHAR(100) NOT NULL COMMENT '证书名称',
  `cert_type`  VARCHAR(20)  DEFAULT NULL COMMENT '类型：vocational / english / computer',
  `issue_date` DATE         DEFAULT NULL COMMENT '获取时间',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='证书表';

DROP TABLE IF EXISTS `job_preferences`;
CREATE TABLE `job_preferences` (
  `id`                   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '偏好ID',
  `user_id`              BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `target_industry`      VARCHAR(100) DEFAULT NULL COMMENT '意向行业',
  `company_type`         VARCHAR(50)  DEFAULT NULL COMMENT '企业类型',
  `accept_overtime`      TINYINT(1) DEFAULT NULL COMMENT '是否接受加班',
  `accept_business_trip` TINYINT(1) DEFAULT NULL COMMENT '是否接受出差',
  `accept_relocation`    TINYINT(1) DEFAULT NULL COMMENT '是否接受异地工作',
  `interview_round_pref` VARCHAR(50) DEFAULT NULL COMMENT '面试轮次偏好：hr / tech / final',
  `interview_style`      VARCHAR(20) DEFAULT NULL COMMENT '面试风格：formal / casual',
  `created_at`           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='求职偏好表';

DROP TABLE IF EXISTS `profile_extras`;
CREATE TABLE `profile_extras` (
  `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id`         BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `self_assessment` TEXT COMMENT '个人优缺点自评',
  `career_plan`     TEXT COMMENT '职业规划与发展方向',
  `hobbies`         TEXT COMMENT '兴趣爱好',
  `specialties`     TEXT COMMENT '个人特长',
  `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='补充信息表';

DROP TABLE IF EXISTS `self_introductions`;
CREATE TABLE `self_introductions` (
  `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '记录ID',
  `user_id`         BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `duration_type`   VARCHAR(20) NOT NULL COMMENT '时长：1min / 3min',
  `scenario`        VARCHAR(20) NOT NULL COMMENT '场景：campus / social / career_change / english',
  `content`         TEXT COMMENT '自我介绍内容',
  `is_ai_generated` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否AI生成：0否 1是',
  `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='智能自我介绍表';

-- ---------- 模拟面试 ----------
DROP TABLE IF EXISTS `interviews`;
CREATE TABLE `interviews` (
  `id`               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '面试ID',
  `user_id`          BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `interview_mode`   VARCHAR(20) NOT NULL COMMENT '模式：one_to_one / group',
  `target_position`  VARCHAR(100) DEFAULT NULL COMMENT '面试岗位',
  `interview_round`  VARCHAR(20) DEFAULT NULL COMMENT '轮次：hr / tech / final',
  `interview_style`  VARCHAR(20) DEFAULT NULL COMMENT '风格：formal / casual',
  `status`           VARCHAR(20) NOT NULL DEFAULT 'ongoing' COMMENT '状态：ongoing / finished / cancelled',
  `total_questions`  INT NOT NULL DEFAULT 0 COMMENT '题目总数',
  `current_question` INT NOT NULL DEFAULT 0 COMMENT '当前题号',
  `total_score`      DECIMAL(5,2) DEFAULT NULL COMMENT '总分',
  `started_at`       DATETIME DEFAULT NULL COMMENT '开始时间',
  `finished_at`      DATETIME DEFAULT NULL COMMENT '结束时间',
  `created_at`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`),
  KEY `idx_user_status` (`user_id`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='面试会话表';

DROP TABLE IF EXISTS `interview_messages`;
CREATE TABLE `interview_messages` (
  `id`              BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `interview_id`    BIGINT UNSIGNED NOT NULL COMMENT '面试ID',
  `role`            VARCHAR(10) NOT NULL COMMENT '角色：ai / user',
  `interviewer_name` VARCHAR(50) DEFAULT NULL COMMENT '面试官标识（群面：A/B/C）',
  `question_index`  INT DEFAULT NULL COMMENT '所属题号',
  `message_type`    VARCHAR(20) DEFAULT NULL COMMENT '类型：question / answer / followup / score',
  `content`         TEXT COMMENT '内容',
  `asr_text`        TEXT COMMENT '语音转文字原文',
  `created_at`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_interview` (`interview_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='面试对话记录表';

DROP TABLE IF EXISTS `interview_feedbacks`;
CREATE TABLE `interview_feedbacks` (
  `id`                   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '点评ID',
  `interview_id`         BIGINT UNSIGNED NOT NULL COMMENT '面试ID',
  `question_index`       INT NOT NULL COMMENT '题号',
  `question_text`        TEXT COMMENT '题目内容',
  `user_answer_summary`  TEXT COMMENT '用户回答摘要',
  `total_score`          DECIMAL(4,1) DEFAULT NULL COMMENT '本题总分',
  `content_score`        DECIMAL(4,1) DEFAULT NULL COMMENT '内容质量分',
  `logic_score`          DECIMAL(4,1) DEFAULT NULL COMMENT '逻辑结构分',
  `expression_score`     DECIMAL(4,1) DEFAULT NULL COMMENT '表达沟通分',
  `professional_score`   DECIMAL(4,1) DEFAULT NULL COMMENT '专业匹配分',
  `highlights`           TEXT COMMENT '亮点',
  `issues`               TEXT COMMENT '主要问题',
  `suggestions`          TEXT COMMENT '改进建议',
  `sample_answer`        TEXT COMMENT '示范回答',
  `created_at`           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_interview` (`interview_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='面试逐题点评表';

DROP TABLE IF EXISTS `interview_reports`;
CREATE TABLE `interview_reports` (
  `id`                        BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '报告ID',
  `interview_id`              BIGINT UNSIGNED NOT NULL COMMENT '面试ID',
  `total_score`               DECIMAL(5,2) DEFAULT NULL COMMENT '总分',
  `overall_comment`           TEXT COMMENT '整体评价',
  `core_suggestions`          TEXT COMMENT '3条核心改进建议',
  `next_practice_suggestions` TEXT COMMENT '下次练习建议',
  `created_at`                DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_interview` (`interview_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='面试报告表';

-- ---------- 简历优化 ----------
DROP TABLE IF EXISTS `resumes`;
CREATE TABLE `resumes` (
  `id`            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '简历ID',
  `user_id`       BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `file_name`     VARCHAR(255) NOT NULL COMMENT '文件名',
  `file_url`      VARCHAR(255) DEFAULT NULL COMMENT '对象存储URL',
  `file_type`     VARCHAR(10)  DEFAULT NULL COMMENT '类型：pdf / word',
  `file_size`     BIGINT       DEFAULT NULL COMMENT '文件大小（字节）',
  `upload_status` VARCHAR(20) NOT NULL DEFAULT 'uploaded' COMMENT '上传状态：uploading / uploaded / failed',
  `parse_status`  VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '解析状态：pending / parsing / done / failed',
  `created_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='简历表';

DROP TABLE IF EXISTS `resume_analyses`;
CREATE TABLE `resume_analyses` (
  `id`                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '分析ID',
  `resume_id`         BIGINT UNSIGNED NOT NULL COMMENT '简历ID',
  `total_score`       DECIMAL(4,1) DEFAULT NULL COMMENT '综合评分',
  `layout_score`      DECIMAL(4,1) DEFAULT NULL COMMENT '排版分',
  `expression_score`  DECIMAL(4,1) DEFAULT NULL COMMENT '表达分',
  `highlight_score`   DECIMAL(4,1) DEFAULT NULL COMMENT '亮点分',
  `match_score`       DECIMAL(4,1) DEFAULT NULL COMMENT '匹配度分',
  `optimized_content` TEXT COMMENT '优化版简历内容',
  `created_at`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_resume` (`resume_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='简历分析结果表';

DROP TABLE IF EXISTS `resume_suggestions`;
CREATE TABLE `resume_suggestions` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '建议ID',
  `analysis_id` BIGINT UNSIGNED NOT NULL COMMENT '分析ID',
  `category`    VARCHAR(20) NOT NULL COMMENT '分类：layout / expression / highlight / match',
  `title`       VARCHAR(255) DEFAULT NULL COMMENT '建议标题',
  `description` TEXT COMMENT '建议内容',
  `created_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_analysis` (`analysis_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='简历优化建议表';

-- ---------- 就业指导 ----------
DROP TABLE IF EXISTS `guidance_chats`;
CREATE TABLE `guidance_chats` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '会话ID',
  `user_id`    BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `chat_type`  VARCHAR(20) NOT NULL COMMENT '类型：companion / other',
  `status`     VARCHAR(20) NOT NULL DEFAULT 'ongoing' COMMENT '状态：ongoing / finished',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='就业指导会话表';

DROP TABLE IF EXISTS `guidance_messages`;
CREATE TABLE `guidance_messages` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息ID',
  `chat_id`    BIGINT UNSIGNED NOT NULL COMMENT '会话ID',
  `role`       VARCHAR(10) NOT NULL COMMENT '角色：ai / user',
  `content`    TEXT COMMENT '内容',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_chat` (`chat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='陪伴/指导消息表';

DROP TABLE IF EXISTS `guidance_contents`;
CREATE TABLE `guidance_contents` (
  `id`           BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '内容ID',
  `title`        VARCHAR(255) NOT NULL COMMENT '标题',
  `content_type` VARCHAR(20) NOT NULL COMMENT '类型：article / music / video',
  `category`     VARCHAR(20) NOT NULL COMMENT '分类：psychology / positive / skill',
  `cover_url`    VARCHAR(255) DEFAULT NULL COMMENT '封面图URL',
  `content_url`  VARCHAR(255) DEFAULT NULL COMMENT '内容地址',
  `status`       TINYINT NOT NULL DEFAULT 1 COMMENT '上架状态：0下架 1上架',
  `created_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_category_status` (`category`, `status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='就业指导内容表';

-- ---------- 商业化 ----------
DROP TABLE IF EXISTS `memberships`;
CREATE TABLE `memberships` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '会员ID',
  `user_id`    BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `plan_type`  VARCHAR(20) NOT NULL COMMENT '套餐：free / vip',
  `start_date` DATETIME DEFAULT NULL COMMENT '生效时间',
  `end_date`   DATETIME DEFAULT NULL COMMENT '到期时间',
  `status`     TINYINT NOT NULL DEFAULT 1 COMMENT '状态：0失效 1生效',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='会员表';

DROP TABLE IF EXISTS `orders`;
CREATE TABLE `orders` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '订单ID',
  `user_id`     BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `order_no`    VARCHAR(64) NOT NULL COMMENT '订单号',
  `plan_type`   VARCHAR(20) NOT NULL COMMENT '套餐类型',
  `amount`      DECIMAL(10,2) NOT NULL COMMENT '金额（元）',
  `pay_status`  TINYINT NOT NULL DEFAULT 0 COMMENT '支付状态：0待支付 1已支付 2已取消',
  `pay_channel` VARCHAR(20) DEFAULT NULL COMMENT '支付渠道：wechat / alipay',
  `paid_at`     DATETIME DEFAULT NULL COMMENT '支付时间',
  `created_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_order_no` (`order_no`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='订单表';

-- ---------- 后期规划（P2） ----------
DROP TABLE IF EXISTS `real_interviews`;
CREATE TABLE `real_interviews` (
  `id`             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '预约ID',
  `user_id`        BIGINT UNSIGNED NOT NULL COMMENT '用户ID',
  `interviewer_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '真人面试官ID',
  `scheduled_at`   DATETIME DEFAULT NULL COMMENT '预约时间',
  `status`         VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT '状态：pending / confirmed / cancelled / finished',
  `created_at`     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='真人模拟面试预约表';

DROP TABLE IF EXISTS `wall_questions`;
CREATE TABLE `wall_questions` (
  `id`         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '问题ID',
  `user_id`    BIGINT UNSIGNED NOT NULL COMMENT '提问用户ID',
  `title`      VARCHAR(255) NOT NULL COMMENT '问题标题',
  `content`    TEXT COMMENT '问题详情',
  `view_count` INT NOT NULL DEFAULT 0 COMMENT '浏览数',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_user` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='真人问答墙问题表';

DROP TABLE IF EXISTS `wall_answers`;
CREATE TABLE `wall_answers` (
  `id`          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '回答ID',
  `question_id` BIGINT UNSIGNED NOT NULL COMMENT '问题ID',
  `answerer_id` BIGINT UNSIGNED DEFAULT NULL COMMENT '回答者ID',
  `content`     TEXT COMMENT '回答内容',
  `created_at`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`),
  KEY `idx_question` (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='真人问答墙回答表';

SET FOREIGN_KEY_CHECKS = 1;
```

---

## 5. 说明

1. **逻辑外键**：本设计只建索引、不建物理外键，业务关联由应用层维护，避免迁移与分表限制。
2. **软删除**：当前未加 `deleted_at`。因涉及个人敏感数据合规（注销后删除），建议注销走**物理删除 + 异步清理对象存储**，暂不引入软删除复杂度。
3. **分表预留**：`interview_messages`、`guidance_messages` 属高频写入表，后续量级增大可按 `interview_id` / `chat_id` 分表或归档。
4. **ORM 对齐**：SQLAlchemy 2.0 async 通过 `asyncmy`（或 `aiomysql`）驱动访问 MySQL；涉及表结构变更时，Alembic 迁移脚本须与本结构保持一致。
