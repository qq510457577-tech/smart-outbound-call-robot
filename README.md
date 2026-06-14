# 智能外呼机器人 (Smart Outbound Call Robot)

基于阿里云 Outbound Bot SDK 构建的自动化外呼系统，提供批量外呼、AI 对话、任务调度和数据统计等完整能力。

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![阿里云](https://img.shields.io/badge/%E9%98%BF%E9%87%8C%E4%BA%91-OutboundBot-orange.svg)

</div>

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 📞 **批量外呼** | 创建任务组、批量拨打、自动重试、CSV 导入 |
| 🤖 **AI 对话** | 实时话术交互、意图识别、多轮对话管理 |
| 📊 **数据统计** | 通话记录、接通率、意图分布、录音下载 |
| 🎯 **智能调度** | 并发控制、工作时段策略、黑/白名单 |
| 🔄 **任务管理** | 暂停/恢复/取消、进度追踪、等待完成回调 |
| 🌐 **Web 控制台** | 可视化操作界面，浏览器直接管理外呼任务 |
| 💬 **RESTful API** | 完整的 HTTP API，便于第三方系统集成 |
| 🧠 **LLM 意图增强** | 支持通义千问等 LLM 提升意图识别准确率 |

## 📂 项目结构

```
smart-outbound-call-robot/
├── src/                          # 核心源代码
│   ├── __init__.py
│   ├── config.py                 # 配置管理 (.env 环境变量)
│   ├── client.py                 # 阿里云 OutboundBot SDK 封装
│   ├── models.py                 # 数据模型定义
│   ├── task_manager.py           # 任务调度与管理
│   └── dialogue.py               # 对话交互与意图识别
├── frontend/                     # Web 控制台
│   ├── index.html                # 主页面
│   ├── styles.css                # 样式表
│   └── app.js                    # 前端逻辑
├── api_server.py                 # Flask API 服务入口
├── examples/                     # 使用示例
│   ├── basic_call.py             # 基础外呼示例
│   ├── batch_jobs.py             # 批量任务示例 (CSV 导入)
│   └── with_scripts.py           # 话术管理示例
├── tests/                        # 单元测试
│   ├── test_api_server.py
│   ├── test_client.py
│   ├── test_task_manager.py
│   ├── test_dialogue.py
│   └── test_models.py
├── docs/                         # 项目文档
├── requirements.txt              # 依赖清单
├── .env.example                  # 环境变量模板
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的阿里云凭据
```

`.env` 文件内容：

```env
ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
ALIBABA_CLOUD_REGION_ID=cn-shanghai
OUTBOUNDBOT_INSTANCE_ID=your_instance_id
DEFAULT_CONCURRENCY=5
MAX_RETRY_TIMES=3
CALL_TIMEOUT_SECONDS=60
```

如需使用 LLM 意图增强：

```env
DASHSCOPE_API_KEY=your_dashscope_api_key
```

### 3. 启动方式

#### 方式一：启动 Web 控制台（推荐）

```bash
# 启动 API 服务
python api_server.py &

# 在浏览器中打开
open http://localhost:5000/frontend/index.html
```

Web 控制台提供可视化的任务管理、话术编辑、对话测试和数据统计功能。

#### 方式二：仅启动 API 服务

```bash
API_PORT=5000 python api_server.py
```

#### 方式三：Python 脚本直接调用

```python
from src.client import OutboundBotClient
from src.task_manager import TaskManager

client = OutboundBotClient()
manager = TaskManager(client)

# 列出实例
instances = client.list_instances()

# 创建批量任务
contacts = [
    {"phone": "13800138001", "name": "张三"},
    {"phone": "13800138002", "name": "李四"},
]

job_group_id = manager.create_batch_job(
    name="回访任务",
    script_id="your_script_id",
    contacts=contacts,
)

manager.start(job_group_id)
progress = manager.get_progress(job_group_id)
print(progress)
```

## 📖 API 文档

### 健康检查

```
GET /health
```

### 实例管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/instances` | 获取实例列表 |
| GET | `/instances/<instance_id>` | 查询实例详情 |

### 话术管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/scripts` | 获取话术列表 |
| POST | `/scripts` | 创建话术 |
| GET | `/scripts/<script_id>` | 查询话术详情 |
| POST | `/scripts/<script_id>/publish` | 发布话术 |

### 任务管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/job-groups` | 获取任务组列表 |
| POST | `/job-groups` | 创建任务组 |
| GET | `/job-groups/<id>` | 查询任务组详情 |
| POST | `/job-groups/<id>/start` | 启动任务 |
| POST | `/job-groups/<id>/pause` | 暂停任务 |
| POST | `/job-groups/<id>/resume` | 恢复任务 |
| POST | `/job-groups/<id>/cancel` | 取消任务 |
| GET | `/job-groups/<id>/progress` | 获取任务进度 |
| GET | `/job-groups/<id>/jobs` | 获取任务列表 |
| POST | `/jobs/batch` | 创建批量外呼任务 |

### 对话交互

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/dialogue` | 发送对话 utterance |
| POST | `/dialogue/analyze-intent` | 分析用户意图 |
| POST | `/dialogue/llm-intent` | LLM 意图识别 |

### 数据统计

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/statistics/<job_group_id>` | 获取任务组统计数据 |
| GET | `/scheduler/status` | 获取调度状态 |
| PUT | `/scheduler/concurrency` | 更新并发数 |

### 其他

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/contacts/whitelist` | 保存白名单 |
| POST | `/contacts/blacklist` | 保存黑名单 |
| GET | `/recordings/<job_id>` | 获取录音下载链接 |

## 📝 示例

### 基础外呼

```bash
python examples/basic_call.py
```

### 批量任务 (CSV 导入)

```bash
# contacts.csv 格式: phone,name
# 13800138001,张三
# 13800138002,李四
python examples/batch_jobs.py
```

### 话术管理

```bash
python examples/with_scripts.py
```

## 🧪 测试

```bash
pytest tests/ -v
```

## 🛠️ 技术栈

- **语言**: Python 3.8+
- **框架**: Flask (API 服务)
- **SDK**: alibabacloud_outboundbot20191226 (阿里云 OutboundBot)
- **LLM**: dashscope (通义千问，可选)
- **前端**: 原生 HTML/CSS/JS
- **配置**: python-dotenv

## ⚙️ 配置说明

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `ALIBABA_CLOUD_ACCESS_KEY_ID` | 阿里云 AccessKey ID | - |
| `ALIBABA_CLOUD_ACCESS_KEY_SECRET` | 阿里云 AccessKey Secret | - |
| `ALIBABA_CLOUD_REGION_ID` | 地域 ID | `cn-shanghai` |
| `OUTBOUNDBOT_INSTANCE_ID` | 外呼机器人实例 ID | - |
| `DEFAULT_CONCURRENCY` | 默认并发数 | `5` |
| `MAX_RETRY_TIMES` | 最大重试次数 | `3` |
| `CALL_TIMEOUT_SECONDS` | 呼叫超时时间(秒) | `60` |
| `DASHSCOPE_API_KEY` | 通义千问 API Key | - |
| `API_PORT` | API 服务端口 | `5000` |

## 📄 License

MIT License
