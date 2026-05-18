"""
任务管理器 - 批量外呼任务的创建、调度与监控
"""
import json
import logging
import time
from typing import List, Dict, Optional, Callable

from .client import OutboundBotClient
from .config import settings

logger = logging.getLogger(__name__)


class TaskManager:
    """外呼任务管理器"""

    def __init__(self, client: Optional[OutboundBotClient] = None):
        self.client = client or OutboundBotClient()
        self._running_tasks: Dict[str, dict] = {}

    def create_batch_job(
        self,
        name: str,
        script_id: str,
        contacts: List[Dict[str, str]],
        strategy: Optional[Dict] = None,
        description: str = "",
    ) -> str:
        """
        创建批量外呼任务

        Args:
            name: 任务名称
            script_id: 话术ID
            contacts: 联系人列表 [{"phone": "138xxx", "name": "张三"}, ...]
            strategy: 外呼策略配置
            description: 任务描述

        Returns:
            job_group_id: 任务组ID
        """
        if strategy is None:
            strategy = self._default_strategy()

        # 构建联系人JSON
        jobs_json = json.dumps([
            {
                "calledNumber": c["phone"],
                "calleeName": c.get("name", ""),
            }
            for c in contacts
        ], ensure_ascii=False)

        # 创建任务组
        result = self.client.create_job_group(
            instance_id=settings.INSTANCE_ID,
            name=name,
            script_id=script_id,
            strategy_json=json.dumps(strategy, ensure_ascii=False),
            description=description,
        )

        job_group_id = result.get("JobGroup", {}).get("JobGroupId", "")
        if job_group_id:
            self._running_tasks[job_group_id] = {
                "name": name,
                "total": len(contacts),
                "status": "created",
                "created_at": time.time(),
            }
        return job_group_id

    def start(self, job_group_id: str) -> bool:
        """启动任务"""
        try:
            self.client.start_job(settings.INSTANCE_ID, job_group_id)
            if job_group_id in self._running_tasks:
                self._running_tasks[job_group_id]["status"] = "running"
            return True
        except Exception as e:
            logger.error(f"启动任务失败 [{job_group_id}]: {e}")
            return False

    def pause(self, job_group_id: str) -> bool:
        """暂停任务"""
        try:
            self.client.suspend_jobs(settings.INSTANCE_ID, job_group_id)
            if job_group_id in self._running_tasks:
                self._running_tasks[job_group_id]["status"] = "paused"
            return True
        except Exception as e:
            logger.error(f"暂停任务失败: {e}")
            return False

    def resume(self, job_group_id: str) -> bool:
        """恢复任务"""
        try:
            self.client.resume_jobs(settings.INSTANCE_ID, job_group_id)
            if job_group_id in self._running_tasks:
                self._running_tasks[job_group_id]["status"] = "running"
            return True
        except Exception as e:
            logger.error(f"恢复任务失败: {e}")
            return False

    def cancel(self, job_group_id: str) -> bool:
        """取消任务"""
        try:
            self.client.cancel_jobs(settings.INSTANCE_ID, job_group_id)
            if job_group_id in self._running_tasks:
                self._running_tasks[job_group_id]["status"] = "cancelled"
            return True
        except Exception as e:
            logger.error(f"取消任务失败: {e}")
            return False

    def get_progress(self, job_group_id: str) -> Dict:
        """获取任务进度"""
        result = self.client.describe_job_group(
            settings.INSTANCE_ID, job_group_id
        )
        job_group = result.get("JobGroup", {})
        progress = job_group.get("Progress", {})
        return {
            "job_group_id": job_group_id,
            "name": job_group.get("JobGroupName", ""),
            "status": job_group.get("Status", ""),
            "total": progress.get("TotalJobs", 0),
            "completed": progress.get("TotalCompleted", 0),
            "pending": progress.get("TotalPending", 0),
            "running": progress.get("TotalRunning", 0),
            "failed": progress.get("TotalFailed", 0),
            "cancelled": progress.get("TotalCancelled", 0),
            "duration": progress.get("Duration", 0),
        }

    def list_jobs(self, job_group_id: str) -> List[Dict]:
        """获取任务组下的所有任务"""
        result = self.client.list_jobs(settings.INSTANCE_ID, job_group_id)
        jobs = result.get("Jobs", [])
        if isinstance(jobs, list):
            return jobs
        return []

    def wait_for_completion(
        self, job_group_id: str,
        interval: int = 10, timeout: int = 3600,
        callback: Optional[Callable] = None,
    ) -> Dict:
        """
        等待任务完成

        Args:
            job_group_id: 任务组ID
            interval: 轮询间隔（秒）
            timeout: 超时时间（秒）
            callback: 进度回调
        """
        start = time.time()
        while time.time() - start < timeout:
            progress = self.get_progress(job_group_id)
            if callback:
                callback(progress)

            status = progress.get("status", "")
            if status in ("Completed", "Cancelled", "Failed"):
                return progress

            time.sleep(interval)

        return {"error": "timeout", "job_group_id": job_group_id}

    @staticmethod
    def _default_strategy() -> Dict:
        """默认外呼策略"""
        return {
            "maxAttemptsPerDay": settings.MAX_RETRY_TIMES,
            "minAttemptInterval": 10,
            "strategyType": "Fixed",
            "workingTime": [
                {"beginTime": "09:00:00", "endTime": "12:00:00"},
                {"beginTime": "13:00:00", "endTime": "18:00:00"},
            ],
            "repeatBy": "Day",
            "followUpStrategy": "None",
        }
