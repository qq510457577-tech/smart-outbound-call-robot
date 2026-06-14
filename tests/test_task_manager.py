"""
TaskManager 单元测试
"""
import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.task_manager import TaskManager
from src.models import JobGroup, Job, Script, Intent, Contact


class MockClient:
    """模拟 OutboundBotClient"""

    def __init__(self):
        pass

    def create_job_group(self, instance_id, name, script_id, strategy_json, description=""):
        return {"JobGroup": {"JobGroupId": "test-job-group-001"}}

    def start_job(self, instance_id, job_group_id):
        return {"success": True}

    def suspend_jobs(self, instance_id, job_group_id):
        return {"success": True}

    def resume_jobs(self, instance_id, job_group_id):
        return {"success": True}

    def cancel_jobs(self, instance_id, job_group_id):
        return {"success": True}

    def describe_job_group(self, instance_id, job_group_id):
        return {
            "JobGroup": {
                "JobGroupName": "测试任务",
                "Status": "Running",
                "Progress": {
                    "TotalJobs": 100,
                    "TotalCompleted": 30,
                    "TotalPending": 60,
                    "TotalRunning": 10,
                    "TotalFailed": 0,
                    "TotalCancelled": 0,
                    "Duration": 120,
                },
            }
        }

    def list_jobs(self, instance_id, job_group_id):
        return {"Jobs": [{"jobId": "j1", "status": "Connected"}]}


class TestTaskManager(unittest.TestCase):
    """TaskManager 测试类"""

    def setUp(self):
        self.client = MockClient()
        self.manager = TaskManager(self.client)

    def test_create_batch_job(self):
        """测试创建批量任务"""
        contacts = [
            {"phone": "13800138001", "name": "张三"},
            {"phone": "13800138002", "name": "李四"},
        ]
        job_group_id = self.manager.create_batch_job(
            name="测试任务", script_id="script-001", contacts=contacts
        )
        self.assertEqual(job_group_id, "test-job-group-001")

    def test_create_batch_job_with_strategy(self):
        """测试使用自定义策略创建任务"""
        contacts = [{"phone": "13800138001"}]
        strategy = {
            "maxAttemptsPerDay": 1,
            "workingTime": [{"beginTime": "10:00:00", "endTime": "12:00:00"}],
        }
        job_group_id = self.manager.create_batch_job(
            name="自定义策略任务", script_id="script-001", contacts=contacts, strategy=strategy
        )
        self.assertEqual(job_group_id, "test-job-group-001")

    def test_start(self):
        """测试启动任务"""
        result = self.manager.start("test-job-group-001")
        self.assertTrue(result)

    def test_pause(self):
        """测试暂停任务"""
        result = self.manager.pause("test-job-group-001")
        self.assertTrue(result)

    def test_resume(self):
        """测试恢复任务"""
        result = self.manager.resume("test-job-group-001")
        self.assertTrue(result)

    def test_cancel(self):
        """测试取消任务"""
        result = self.manager.cancel("test-job-group-001")
        self.assertTrue(result)

    def test_get_progress(self):
        """测试获取任务进度"""
        progress = self.manager.get_progress("test-job-group-001")
        self.assertEqual(progress["job_group_id"], "test-job-group-001")
        self.assertEqual(progress["name"], "测试任务")
        self.assertEqual(progress["status"], "Running")
        self.assertEqual(progress["total"], 100)
        self.assertEqual(progress["completed"], 30)

    def test_list_jobs(self):
        """测试获取任务列表"""
        jobs = self.manager.list_jobs("test-job-group-001")
        self.assertIsInstance(jobs, list)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["jobId"], "j1")

    def test_default_strategy(self):
        """测试默认策略"""
        strategy = TaskManager._default_strategy()
        self.assertIn("maxAttemptsPerDay", strategy)
        self.assertIn("workingTime", strategy)
        self.assertIn("strategyType", strategy)


if __name__ == "__main__":
    unittest.main()
