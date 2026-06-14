# 架构设计

## 整体架构

```
┌─────────────────────────────────────────────────────┐
│                   浏览器 (Web 控制台)                  │
│              frontend/index.html + app.js             │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP REST API
┌──────────────────────▼──────────────────────────────┐
│              Flask API 服务 (api_server.py)           │
│  ┌────────────┐ ┌────────────┐ ┌─────────────────┐  │
│  │ 实例管理    │ │ 话术管理    │ │  任务调度管理     │  │
│  └────────────┘ └────────────┘ └─────────────────┘  │
│  ┌────────────┐ ┌────────────┐ ┌─────────────────┐  │
│  │ 对话交互    │ │ 数据统计    │ │  LLM 意图增强    │  │
│  └────────────┘ └────────────┘ └─────────────────┘  │
└──────────────────────┬──────────────────────────────┘
                       │ 阿里云 SDK
┌──────────────────────▼──────────────────────────────┐
│         阿里云 OutboundBot API                       │
│  外呼实例 / 话术 / 任务 / 通话 / 意图 / 录音          │
└─────────────────────────────────────────────────────┘
```

## 核心组件

### 1. OutboundBotClient (`src/client.py`)

对阿里云 OutboundBot SDK 的封装，提供所有 API 的 Python 调用接口。

- 管理阿里云认证（AK/SK）
- 封装实例管理、话术管理、任务管理、意图管理、黑/白名单、录音下载、对话交互等接口
- 统一返回值格式（SDK 对象 → dict）

### 2. TaskManager (`src/task_manager.py`)

外呼任务的高级管理模块，封装了任务创建、启停、进度轮询和批量操作逻辑。

- 批量任务创建（联系人列表 → 任务组 → 自动启动）
- 任务生命周期管理（created → running → completed/paused/cancelled/failed）
- 进度轮询和回调机制
- 默认外呼策略（工作时段、重试策略）

### 3. DialogueManager (`src/dialogue.py`)

实时对话交互管理，处理用户 utterance 发送和意图识别。

- 通过阿里云实时对话接口发送 utterance
- 基于关键词的意图识别
- 预留 LLM 增强接口（通义千问）

### 4. DataModels (`src/models.py`)

数据模型定义，包括 JobGroup、Job、Script、Intent、Contact、CallRecord、DialogueFlow、AgentProfile 等。

## 数据流

```
用户操作 (Web/API)
    │
    ▼
api_server.py 路由分发
    │
    ├── 实例/话术管理 ───► OutboundBotClient ───► 阿里云 API
    ├── 任务管理    ───► TaskManager    ───► OutboundBotClient ───► 阿里云 API
    ├── 对话交互    ───► DialogueManager ───► OutboundBotClient ───► 阿里云 API
    └── 数据统计    ───► 聚合 TaskManager 数据 ───► 返回统计结果
```

## 部署架构

```
开发/测试环境:
  单机部署 — Flask 直接运行

生产环境建议:
  nginx (反向代理/静态文件)
    └── gunicorn (WSGI 服务)
        └── api_server.py (Flask 应用)
```
