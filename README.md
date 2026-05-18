# 智能外呼机器人

基于阿里云 Outbound Bot（智能外呼机器人）API 构建的自动化外呼系统。

## 功能

- 📞 **批量外呼** — 创建任务、批量拨打、自动重试
- 🤖 **AI 对话** — 话术管理、意图识别、多轮对话
- 📊 **数据统计** — 通话记录、接通率、意图统计
- 🎯 **智能调度** — 并发控制、时段策略、黑/白名单
- 🔄 **任务管理** — 暂停/恢复/取消、进度追踪

## 快速开始

### 1. 安装

```bash
pip install alibabacloud_outboundbot20191226
```

### 2. 配置

```bash
export ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_secret
export ALIBABA_CLOUD_REGION_ID=cn-shanghai
# 或使用 .env 文件
```

### 3. 使用

```python
from src.client import OutboundBotClient

client = OutboundBotClient()

# 列出实例
instances = client.list_instances()
print(instances)

# 创建外呼任务
job = client.create_job_group(
    name="回访任务-20240518",
    strategy_json={...}
)
```

## 项目结构

```
smart-outbound-call-robot/
├── src/
│   ├── __init__.py
│   ├── client.py          # 阿里云 SDK 封装
│   ├── models.py          # 数据模型
│   ├── task_manager.py    # 任务管理
│   ├── dialogue.py        # 对话管理
│   └── config.py          # 配置管理
├── examples/
│   ├── basic_call.py      # 基础外呼示例
│   ├── batch_jobs.py      # 批量任务示例
│   └── with_scripts.py    # 话术管理示例
├── tests/
│   └── test_client.py
├── requirements.txt
├── .env.example
└── README.md
```
