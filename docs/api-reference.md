# API 接口文档

所有接口返回 JSON 格式，基础路径为 `http://localhost:5000`。

## 通用说明

- 除 GET 请求外，POST/PUT 请求需设置 `Content-Type: application/json`
- 错误响应格式: `{"error": "错误信息"}` 或 `{"success": false, "message": "详情"}`

---

## 1. 健康检查

```
GET /health
```

**响应示例:**
```json
{
  "status": "ok",
  "timestamp": "2024-05-20T10:30:00",
  "region": "cn-shanghai"
}
```

---

## 2. 实例管理

### 获取实例列表

```
GET /instances
```

**响应:** 阿里云 `ListInstances` 返回数据

### 查询实例详情

```
GET /instances/{instance_id}
```

---

## 3. 话术管理

### 获取话术列表

```
GET /scripts?instance_id=xxx
```

### 创建话术

```
POST /scripts
Content-Type: application/json

{
  "instance_id": "xxx",
  "name": "客户回访-v2",
  "script_content": "{ ... JSON 格式的话术内容 ... }",
  "script_description": "2024年Q2版本"
}
```

### 查询话术详情

```
GET /scripts/{script_id}
Content-Type: application/json
{ "instance_id": "xxx" }
```

### 发布话术

```
POST /scripts/{script_id}/publish
Content-Type: application/json
{ "instance_id": "xxx" }
```

---

## 4. 任务管理

### 获取任务组列表

```
GET /job-groups?instance_id=xxx
```

### 创建任务组

```
POST /job-groups
Content-Type: application/json

{
  "instance_id": "xxx",
  "name": "回访任务-20240518",
  "script_id": "script_xxx",
  "strategy_json": "{ ... 外呼策略 JSON ... }",
  "description": "描述信息",
  "recall_strategy_json": "{ ... 重呼策略 JSON (可选) ... }"
}
```

**默认策略:**
```json
{
  "maxAttemptsPerDay": 3,
  "minAttemptInterval": 10,
  "strategyType": "Fixed",
  "workingTime": [
    {"beginTime": "09:00:00", "endTime": "12:00:00"},
    {"beginTime": "13:00:00", "endTime": "18:00:00"}
  ],
  "repeatBy": "Day",
  "followUpStrategy": "None"
}
```

### 任务控制

| 操作 | 方法 | 路径 |
|------|------|------|
| 启动 | POST | `/job-groups/{id}/start` |
| 暂停 | POST | `/job-groups/{id}/pause` |
| 恢复 | POST | `/job-groups/{id}/resume` |
| 取消 | POST | `/job-groups/{id}/cancel` |

响应: `{"success": true}`

### 获取进度

```
GET /job-groups/{id}/progress
```

**响应:**
```json
{
  "job_group_id": "jg_xxx",
  "name": "回访任务",
  "status": "Running",
  "total": 100,
  "completed": 45,
  "pending": 50,
  "running": 5,
  "failed": 0,
  "cancelled": 0,
  "duration": 3600
}
```

### 获取任务列表

```
GET /job-groups/{id}/jobs
```

### 创建批量任务

```
POST /jobs/batch
Content-Type: application/json

{
  "name": "批量外呼-0520",
  "script_id": "script_xxx",
  "contacts": [
    {"phone": "13800138001", "name": "张三"},
    {"phone": "13800138002", "name": "李四"}
  ],
  "strategy": "{ ... 可选 ... }",
  "description": "可选描述"
}
```

**响应:**
```json
{
  "job_group_id": "jg_xxx",
  "total": 2
}
```

---

## 5. 对话交互

### 发送对话

```
POST /dialogue
Content-Type: application/json

{
  "session_id": "sess_xxx",
  "utterance": "我需要考虑一下",
  "calling_number": "13800138000",
  "called_number": "13900139000"
}
```

### 分析意图（关键词匹配）

```
POST /dialogue/analyze-intent
Content-Type: application/json

{ "text": "我需要考虑一下" }
```

**响应:** `{"text": "我需要考虑一下", "intent": "CONSIDERING"}`

### LLM 意图识别

```
POST /dialogue/llm-intent
Content-Type: application/json

{
  "text": "我需要考虑一下，下周再联系吧",
  "context": "外呼销售场景"
}
```

**响应:**
```json
{
  "text": "我需要考虑一下，下周再联系吧",
  "intent": "CONSIDERING",
  "source": "llm"
}
```

---

## 6. 数据统计

### 获取任务组统计

```
GET /statistics/{job_group_id}
```

**响应:**
```json
{
  "job_group_id": "jg_xxx",
  "total_jobs": 100,
  "completed_jobs": 85,
  "failed_jobs": 5,
  "pending_jobs": 10,
  "running_jobs": 0,
  "cancelled_jobs": 0,
  "completion_rate": 85.0,
  "success_rate": 94.44,
  "average_duration_seconds": 120.5,
  "status_distribution": {"Completed": 85, "Failed": 5, "Pending": 10},
  "status_from_progress": {
    "completed": 85,
    "pending": 10,
    "running": 0,
    "failed": 5,
    "cancelled": 0
  }
}
```

---

## 7. 调度管理

### 获取调度状态

```
GET /scheduler/status
```

**响应:**
```json
{
  "running_tasks": 2,
  "tasks": ["jg_xxx", "jg_yyy"],
  "max_concurrency": 5
}
```

### 更新并发数

```
PUT /scheduler/concurrency
Content-Type: application/json

{ "concurrency": 10 }
```

---

## 8. 黑名单/白名单

### 保存白名单

```
POST /contacts/whitelist
Content-Type: application/json

{
  "instance_id": "xxx",
  "contact_list": "[{\"contactPhone\":\"13800138001\"}]"
}
```

### 保存黑名单

```
POST /contacts/blacklist
Content-Type: application/json

{
  "instance_id": "xxx",
  "contact_list": "[{\"contactPhone\":\"13800138001\"}]"
}
```

---

## 9. 录音下载

```
GET /recordings/{task_id}
Content-Type: application/json
{
  "instance_id": "xxx",
  "need_voice_slice_recording": false,
  "swap_channels": false
}
```

---

## 错误码

| HTTP 状态码 | 说明 |
|------------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 500 | 服务器错误 (任务执行失败等) |
