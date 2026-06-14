"""
API 服务层单元测试
"""
import json
import unittest
from unittest.mock import patch, MagicMock

# 需要先 mock 配置再导入 app
with patch.dict("os.environ", {
    "ALIBABA_CLOUD_ACCESS_KEY_ID": "test-key",
    "ALIBABA_CLOUD_ACCESS_KEY_SECRET": "test-secret",
    "ALIBABA_CLOUD_REGION_ID": "cn-shanghai",
    "OUTBOUNDBOT_INSTANCE_ID": "inst-test-001",
}):
    from api_server import app


class TestHealthEndpoint(unittest.TestCase):
    """健康检查测试"""

    def setUp(self):
        self.client = app.test_client()

    def test_health(self):
        """测试健康检查接口"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["status"], "ok")
        self.assertIn("timestamp", data)
        self.assertIn("region", data)


class TestJobEndpoints(unittest.TestCase):
    """任务相关接口测试"""

    def setUp(self):
        self.client = app.test_client()

    @patch("api_server.task_manager")
    def test_get_progress(self, mock_tm):
        """测试获取任务进度接口"""
        mock_tm.get_progress.return_value = {
            "job_group_id": "jg-001",
            "name": "测试任务",
            "status": "Running",
            "total": 100,
            "completed": 30,
            "pending": 60,
            "running": 10,
            "failed": 0,
            "cancelled": 0,
        }

        resp = self.client.get("/job-groups/jg-001/progress")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["job_group_id"], "jg-001")
        self.assertEqual(data["total"], 100)

    @patch("api_server.task_manager")
    def test_start_job_group(self, mock_tm):
        """测试启动任务组接口"""
        mock_tm.start.return_value = True
        resp = self.client.post("/job-groups/jg-001/start")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertTrue(data["success"])

    @patch("api_server.task_manager")
    def test_start_job_group_failure(self, mock_tm):
        """测试启动任务组失败"""
        mock_tm.start.return_value = False
        resp = self.client.post("/job-groups/jg-001/start")
        self.assertEqual(resp.status_code, 500)

    @patch("api_server.task_manager")
    def test_pause_job_group(self, mock_tm):
        """测试暂停任务组接口"""
        mock_tm.pause.return_value = True
        resp = self.client.post("/job-groups/jg-001/pause")
        self.assertEqual(resp.status_code, 200)

    @patch("api_server.task_manager")
    def test_resume_job_group(self, mock_tm):
        """测试恢复任务组接口"""
        mock_tm.resume.return_value = True
        resp = self.client.post("/job-groups/jg-001/resume")
        self.assertEqual(resp.status_code, 200)

    @patch("api_server.task_manager")
    def test_cancel_job_group(self, mock_tm):
        """测试取消任务组接口"""
        mock_tm.cancel.return_value = True
        resp = self.client.post("/job-groups/jg-001/cancel")
        self.assertEqual(resp.status_code, 200)


class TestBatchJobEndpoint(unittest.TestCase):
    """批量任务创建接口测试"""

    def setUp(self):
        self.client = app.test_client()

    @patch("api_server.task_manager")
    def test_create_batch_job(self, mock_tm):
        """测试批量任务创建接口"""
        mock_tm.create_batch_job.return_value = "jg-batch-001"
        payload = {
            "name": "批量外呼测试",
            "script_id": "script-001",
            "contacts": [
                {"phone": "13800138001", "name": "张三"},
                {"phone": "13800138002", "name": "李四"},
            ],
        }
        resp = self.client.post(
            "/jobs/batch",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 201)
        data = json.loads(resp.data)
        self.assertEqual(data["job_group_id"], "jg-batch-001")
        self.assertEqual(data["total"], 2)


class TestStatisticsEndpoint(unittest.TestCase):
    """统计数据接口测试"""

    def setUp(self):
        self.client = app.test_client()

    @patch("api_server.task_manager")
    def test_get_statistics(self, mock_tm):
        """测试获取统计数据接口"""
        mock_tm.get_progress.return_value = {
            "total": 100, "completed": 80, "failed": 10,
            "pending": 5, "running": 5, "cancelled": 0,
        }
        mock_tm.list_jobs.return_value = [
            {"jobId": "j1", "status": "Completed", "duration": 120},
            {"jobId": "j2", "status": "Completed", "duration": 60},
            {"jobId": "j3", "status": "Failed", "duration": 30},
            {"jobId": "j4", "status": "Pending", "duration": 0},
        ]

        resp = self.client.get("/statistics/jg-001")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["total_jobs"], 100)
        self.assertEqual(data["completed_jobs"], 80)
        self.assertIn("completion_rate", data)
        self.assertIn("average_duration_seconds", data)


class TestDialogueEndpoints(unittest.TestCase):
    """对话接口测试"""

    def setUp(self):
        self.client = app.test_client()

    @patch("api_server.dialogue_manager")
    def test_send_dialogue(self, mock_dm):
        """测试对话交互接口"""
        mock_dm.send_utterance.return_value = {
            "dialogue": {"intent": "INTENT_OK", "response": "谢谢"}
        }
        payload = {
            "session_id": "session-001",
            "utterance": "你好",
            "calling_number": "021-12345678",
            "called_number": "13800138000",
        }
        resp = self.client.post(
            "/dialogue",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

    @patch("api_server.dialogue_manager")
    def test_analyze_intent(self, mock_dm):
        """测试意图分析接口"""
        mock_dm.analyze_intent.return_value = "INTERESTED"
        payload = {"text": "我很有意向"}
        resp = self.client.post(
            "/dialogue/analyze-intent",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["intent"], "INTERESTED")


class TestSchedulerEndpoints(unittest.TestCase):
    """调度器接口测试"""

    def setUp(self):
        self.client = app.test_client()

    def test_scheduler_status(self):
        """测试调度状态接口"""
        resp = self.client.get("/scheduler/status")
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertIn("running_tasks", data)
        self.assertIn("max_concurrency", data)

    def test_update_concurrency(self):
        """测试更新并发数接口"""
        resp = self.client.put(
            "/scheduler/concurrency",
            data=json.dumps({"concurrency": 10}),
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.data)
        self.assertEqual(data["concurrency"], 10)


if __name__ == "__main__":
    unittest.main()
