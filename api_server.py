"""
智能外呼机器人 API 服务层
基于 Flask 提供 RESTful API，封装所有阿里云 Outbound Bot 能力
"""
import json
import logging
import os
from datetime import datetime
from typing import Optional

from flask import Flask, request, jsonify

from src.client import OutboundBotClient
from src.task_manager import TaskManager
from src.dialogue import DialogueManager
from src.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 静态文件服务：frontend/ 目录下的 HTML/CSS
STATIC_DIR = os.path.join(os.path.dirname(__file__), "frontend")

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="/frontend")

# 全局单例
client = OutboundBotClient()
task_manager = TaskManager(client)
dialogue_manager = DialogueManager(client)


# ─── 全局错误处理 ───────────────────────────────────

@app.errorhandler(500)
def handle_500(error):
    """将 500 错误转换为 JSON 响应"""
    return jsonify({
        "error": str(error),
        "message": "服务器内部错误，请检查阿里云凭据配置",
    }), 500

@app.errorhandler(404)
def handle_404(error):
    return jsonify({"error": "Not Found", "message": str(error)}), 404

# ─── 健康检查 ───────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """健康检查"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "region": settings.REGION_ID,
    })


# ─── 实例管理 ───────────────────────────────────────

def _api(f):
    """通用 API 装饰器：捕获 SDK 异常，返回 JSON 错误"""
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"API 错误 [{request.path}]: {e}")
            return jsonify({
                "error": str(e),
                "message": "请求失败，请检查配置或稍后重试",
            }), 500
    return wrapper


@app.route("/instances", methods=["GET"])
@_api
def list_instances():
    """获取外呼机器人实例列表"""
    result = client.list_instances()
    return jsonify(result)


@app.route("/instances/<instance_id>", methods=["GET"])
@_api
def describe_instance(instance_id: str):
    """查询实例详情"""
    result = client.describe_instance(instance_id)
    return jsonify(result)


# ─── 话术管理 ───────────────────────────────────────

@app.route("/scripts", methods=["GET"])
@_api
def list_scripts():
    """获取话术列表"""
    instance_id = request.args.get("instance_id", settings.INSTANCE_ID)
    result = client.list_scripts(instance_id)
    return jsonify(result)


@app.route("/scripts", methods=["POST"])
@_api
def create_script():
    """创建话术"""
    data = request.get_json()
    instance_id = data.get("instance_id", settings.INSTANCE_ID)
    name = data["name"]
    script_content = data["script_content"]
    description = data.get("script_description", "")

    result = client.create_script(instance_id, name, script_content, description)
    return jsonify(result), 201


@app.route("/scripts/<script_id>", methods=["GET"])
@_api
def describe_script(script_id: str):
    """查询话术详情"""
    data = request.get_json(silent=True) or {}
    instance_id = data.get("instance_id", settings.INSTANCE_ID)
    result = client.describe_script(instance_id, script_id)
    return jsonify(result)


@app.route("/scripts/<script_id>/publish", methods=["POST"])
@_api
def publish_script(script_id: str):
    """发布话术"""
    data = request.get_json(silent=True) or {}
    instance_id = data.get("instance_id", settings.INSTANCE_ID)
    result = client.publish_script(instance_id, script_id)
    return jsonify(result)


# ─── 任务组管理 ─────────────────────────────────────

@app.route("/job-groups", methods=["GET"])
@_api
def list_job_groups():
    """获取任务组列表"""
    instance_id = request.args.get("instance_id", settings.INSTANCE_ID)
    result = client.list_job_groups(instance_id)
    return jsonify(result)


@app.route("/job-groups", methods=["POST"])
@_api
def create_job_group():
    """创建任务组"""
    data = request.get_json()
    instance_id = data.get("instance_id", settings.INSTANCE_ID)
    name = data["name"]
    script_id = data["script_id"]
    strategy_json = data.get("strategy_json", json.dumps(task_manager._default_strategy()))
    description = data.get("description", "")
    recall_strategy_json = data.get("recall_strategy_json")

    result = client.create_job_group(
        instance_id, name, script_id, strategy_json,
        description, recall_strategy_json
    )
    return jsonify(result), 201


@app.route("/job-groups/<job_group_id>", methods=["GET"])
@_api
def describe_job_group(job_group_id: str):
    """查询任务组详情"""
    data = request.get_json(silent=True) or {}
    instance_id = data.get("instance_id", settings.INSTANCE_ID)
    result = client.describe_job_group(instance_id, job_group_id)
    return jsonify(result)


# ─── 任务控制 ───────────────────────────────────────

@app.route("/job-groups/<job_group_id>/start", methods=["POST"])
@_api
def start_job_group(job_group_id: str):
    """启动任务组"""
    result = task_manager.start(job_group_id)
    status_code = 200 if result else 500
    return jsonify({"success": result}), status_code


@app.route("/job-groups/<job_group_id>/pause", methods=["POST"])
@_api
def pause_job_group(job_group_id: str):
    """暂停任务组"""
    result = task_manager.pause(job_group_id)
    status_code = 200 if result else 500
    return jsonify({"success": result}), status_code


@app.route("/job-groups/<job_group_id>/resume", methods=["POST"])
@_api
def resume_job_group(job_group_id: str):
    """恢复任务组"""
    result = task_manager.resume(job_group_id)
    status_code = 200 if result else 500
    return jsonify({"success": result}), status_code


@app.route("/job-groups/<job_group_id>/cancel", methods=["POST"])
@_api
def cancel_job_group(job_group_id: str):
    """取消任务组"""
    result = task_manager.cancel(job_group_id)
    status_code = 200 if result else 500
    return jsonify({"success": result}), status_code


# ─── 任务进度 ───────────────────────────────────────

@app.route("/job-groups/<job_group_id>/progress", methods=["GET"])
@_api
def get_job_progress(job_group_id: str):
    """获取任务进度"""
    progress = task_manager.get_progress(job_group_id)
    return jsonify(progress)


@app.route("/job-groups/<job_group_id>/jobs", methods=["GET"])
@_api
def list_jobs(job_group_id: str):
    """获取任务列表"""
    jobs = task_manager.list_jobs(job_group_id)
    return jsonify({"jobs": jobs})


# ─── 批量任务创建 ───────────────────────────────────

@app.route("/jobs/batch", methods=["POST"])
@_api
def create_batch_job():
    """创建批量外呼任务"""
    data = request.get_json()
    name = data["name"]
    script_id = data["script_id"]
    contacts = data["contacts"]  # [{"phone": "138xxx", "name": "张三"}]
    strategy = data.get("strategy")
    description = data.get("description", "")

    job_group_id = task_manager.create_batch_job(
        name, script_id, contacts, strategy, description
    )
    return jsonify({"job_group_id": job_group_id, "total": len(contacts)}), 201


# ─── 通话对话 ───────────────────────────────────────

@app.route("/dialogue", methods=["POST"])
@_api
def send_dialogue():
    """发送对话 utterance 并获取 AI 回复"""
    data = request.get_json()
    session_id = data["session_id"]
    utterance = data["utterance"]
    calling_number = data["calling_number"]
    called_number = data["called_number"]

    result = dialogue_manager.send_utterance(
        session_id, utterance, calling_number, called_number
    )
    return jsonify(result)


@app.route("/dialogue/analyze-intent", methods=["POST"])
@_api
def analyze_intent():
    """分析用户意图"""
    data = request.get_json()
    text = data["text"]
    intent = dialogue_manager.analyze_intent(text)
    return jsonify({"text": text, "intent": intent})


# ─── 黑/白名单 ──────────────────────────────────────

@app.route("/contacts/whitelist", methods=["POST"])
@_api
def save_whitelist():
    """保存白名单"""
    data = request.get_json()
    instance_id = data.get("instance_id", settings.INSTANCE_ID)
    contact_list = data["contact_list"]  # JSON 格式字符串
    result = client.save_contact_white_list(instance_id, contact_list)
    return jsonify(result)


@app.route("/contacts/blacklist", methods=["POST"])
@_api
def save_blacklist():
    """保存黑名单"""
    data = request.get_json()
    instance_id = data.get("instance_id", settings.INSTANCE_ID)
    contact_list = data["contact_list"]
    result = client.save_contact_block_list(instance_id, contact_list)
    return jsonify(result)


# ─── 录音下载 ───────────────────────────────────────

@app.route("/recordings/<job_id>", methods=["GET"])
@_api
def get_recording(job_id: str):
    """获取录音下载链接

    Args:
        job_id: 实际传入 task_id (SDK 参数名)
    """
    data = request.get_json(silent=True) or {}
    instance_id = data.get("instance_id", settings.INSTANCE_ID)
    need_voice_slice = data.get("need_voice_slice_recording", False)
    swap = data.get("swap_channels", False)
    result = client.download_recording(instance_id, job_id, need_voice_slice, swap)
    return jsonify(result)


# ─── 数据统计 ───────────────────────────────────────

@app.route("/statistics/<job_group_id>", methods=["GET"])
@_api
def get_statistics(job_group_id: str):
    """
    获取任务组统计数据
    包括: 总任务数、完成率、平均通话时长、各状态分布
    """
    progress = task_manager.get_progress(job_group_id)
    jobs = task_manager.list_jobs(job_group_id)

    # 按状态分组统计
    status_counts = {}
    total_duration = 0
    duration_count = 0

    for job in jobs:
        status = job.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        dur = job.get("duration", 0)
        if dur > 0:
            total_duration += dur
            duration_count += 1

    avg_duration = total_duration / duration_count if duration_count > 0 else 0
    total = progress.get("total", 0)
    completed = progress.get("completed", 0)
    failed = progress.get("failed", 0)

    statistics = {
        "job_group_id": job_group_id,
        "total_jobs": total,
        "completed_jobs": completed,
        "failed_jobs": failed,
        "pending_jobs": progress.get("pending", 0),
        "running_jobs": progress.get("running", 0),
        "cancelled_jobs": progress.get("cancelled", 0),
        "completion_rate": round(completed / total * 100, 2) if total > 0 else 0,
        "success_rate": round(
            completed / (completed + failed) * 100, 2
        ) if (completed + failed) > 0 else 0,
        "average_duration_seconds": round(avg_duration, 2),
        "status_distribution": status_counts,
        "status_from_progress": {
            "completed": progress.get("completed", 0),
            "pending": progress.get("pending", 0),
            "running": progress.get("running", 0),
            "failed": progress.get("failed", 0),
            "cancelled": progress.get("cancelled", 0),
        },
    }
    return jsonify(statistics)


# ─── LLM 意图增强 ───────────────────────────────────

@app.route("/dialogue/llm-intent", methods=["POST"])
def llm_intent():
    """
    使用 LLM（通义千问等）增强意图识别
    替代简单的关键词匹配

    Body: {
        "text": "我需要考虑一下，下周再联系吧",
        "context": "外呼销售场景"
    }
    """
    data = request.get_json()
    text = data.get("text", "")
    context = data.get("context", "")

    try:
        # 尝试使用通义千问 API
        intent = _llm_analyze(text, context)
        return jsonify({
            "text": text,
            "intent": intent,
            "source": "llm",
        })
    except ImportError:
        # 如果没有 dashscope，回退到关键词匹配
        logger.warning("dashscope 未安装，回退到关键词匹配")
        intent = dialogue_manager.analyze_intent(text)
        return jsonify({
            "text": text,
            "intent": intent,
            "source": "keyword_match",
        })
    except Exception as e:
        logger.error(f"LLM 意图识别失败: {e}")
        intent = dialogue_manager.analyze_intent(text)
        return jsonify({
            "text": text,
            "intent": intent,
            "source": "keyword_match_fallback",
            "error": str(e),
        })


def _llm_analyze(text: str, context: str) -> str:
    """调用通义千问进行意图分析"""
    import os

    try:
        import dashscope
        from dashscope.api_entities.dashscope_response import Role

        dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

        prompt = f"""
        你是一个意图识别助手。根据以下对话内容和上下文，判断用户的意图。

        上下文: {context}
        用户输入: {text}

        请从以下类别中选择一个最合适的意图:
        - INTERESTED: 用户表现出明确兴趣
        - CONSIDERING: 用户需要时间考虑
        - NOT_INTERESTED: 用户明确表示不感兴趣
        - REJECTED: 用户拒绝继续通话
        - CALL_BACK: 用户要求稍后联系
        - AGREED: 用户同意某项建议
        - OTHER: 其他意图

        只返回意图类别名称，不要其他内容。
        """

        response = dashscope.Generation.call(
            model="qwen-turbo",
            messages=[{"role": Role.SYSTEM, "content": prompt}],
        )

        if response.status_code == 200:
            intent = response.output.text.strip()
            return intent
        else:
            raise ValueError(f"dashscope error: {response.code}")

    except ImportError:
        raise ImportError("dashscope 未安装，请运行: pip install dashscope")


# ─── 并发调度 ───────────────────────────────────────

@app.route("/scheduler/status", methods=["GET"])
def scheduler_status():
    """获取当前调度状态"""
    return jsonify({
        "running_tasks": len(task_manager._running_tasks),
        "tasks": list(task_manager._running_tasks.keys()),
        "max_concurrency": settings.DEFAULT_CONCURRENCY,
    })


@app.route("/scheduler/concurrency", methods=["PUT"])
def update_concurrency():
    """更新并发数配置"""
    data = request.get_json()
    new_concurrency = data.get("concurrency", settings.DEFAULT_CONCURRENCY)
    settings.DEFAULT_CONCURRENCY = new_concurrency
    return jsonify({
        "message": f"并发数已更新为 {new_concurrency}",
        "concurrency": new_concurrency,
    })


# ─── 启动入口 ───────────────────────────────────────

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    # 根路径重定向到 Web 控制台
    @app.route("/")
    def index():
        from flask import redirect
        return redirect("/frontend/index.html")
    app.run(host="0.0.0.0", port=port, debug=debug)
