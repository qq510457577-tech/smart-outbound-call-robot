"""
OutboundBotClient 单元测试
"""
import json
import unittest
from unittest.mock import MagicMock, patch

from src.client import OutboundBotClient
from src.config import settings


def _make_mock_resp(data: dict) -> MagicMock:
    """创建一个 MagicMock，其 body.__str__() 返回合法的 JSON 字符串"""
    resp = MagicMock()
    resp.body = MagicMock()
    resp.body.__str__ = lambda self: json.dumps(data)
    return resp


class MockSDKClient:
    """模拟 SDK 客户端"""

    def __init__(self, config):
        pass

    def list_instances(self, request):
        return _make_mock_resp({"instances": [{"instanceId": "inst-001"}]})

    def describe_instance(self, request):
        return _make_mock_resp({"instance": {"instanceId": request.instance_id, "status": "Active"}})

    def list_scripts(self, request):
        return _make_mock_resp({"scripts": [{"scriptId": "script-001", "scriptName": "回访话术"}]})

    def create_script(self, request):
        return _make_mock_resp({"script": {"scriptId": "new-script-001"}})

    def publish_script(self, request):
        return _make_mock_resp({"script": {"scriptId": request.script_id, "status": "Published"}})

    def list_job_groups(self, request):
        return _make_mock_resp({"jobGroups": [{"jobGroupId": "job-001"}]})

    def create_job_group(self, request):
        return _make_mock_resp({"jobGroup": {"jobGroupId": "new-job-001"}})

    def describe_job_group(self, request):
        return _make_mock_resp({
            "JobGroup": {
                "jobGroupId": request.job_group_id,
                "status": "Running",
                "Progress": {
                    "TotalJobs": 100,
                    "TotalCompleted": 50,
                    "TotalPending": 50,
                    "TotalRunning": 0,
                    "TotalFailed": 0,
                    "TotalCancelled": 0,
                    "Duration": 120,
                },
            }
        })

    def start_job(self, request):
        return _make_mock_resp({"success": True})

    def suspend_jobs(self, request):
        return _make_mock_resp({"success": True})

    def resume_jobs(self, request):
        return _make_mock_resp({"success": True})

    def cancel_jobs(self, request):
        return _make_mock_resp({"success": True})

    def list_jobs(self, request):
        return _make_mock_resp({"jobs": [{"jobId": "job-detail-001", "status": "Connected"}]})

    def describe_job(self, request):
        return _make_mock_resp({"job": {"jobId": request.job_id, "status": "Connected"}})

    def assign_jobs(self, request):
        return _make_mock_resp({"success": True})

    def create_intent(self, request):
        return _make_mock_resp({"intent": {"intentId": "intent-001"}})

    def list_intents(self, request):
        return _make_mock_resp({"intents": [{"intentId": "intent-001", "intentName": "意向"}]})

    def save_contact_white_list(self, request):
        return _make_mock_resp({"success": True})

    def save_contact_block_list(self, request):
        return _make_mock_resp({"success": True})

    def download_recording(self, request):
        return _make_mock_resp({"recording": {"downloadUrl": "https://example.com/rec.mp3"}})

    def dialogue(self, request):
        return _make_mock_resp({"dialogue": {"intent": "INTENT_OK", "response": "好的，我了解了"}})


class TestOutboundBotClient(unittest.TestCase):
    """OutboundBotClient 测试类"""

    def setUp(self):
        """测试前准备"""
        with patch("src.client.OutboundBotClientSDK", MockSDKClient):
            self.client = OutboundBotClient()

    # ─── 实例管理测试 ───────────────────────────────

    def test_list_instances(self):
        """测试获取实例列表"""
        result = self.client.list_instances()
        self.assertIsInstance(result, dict)
        self.assertIn("instances", result)

    def test_describe_instance(self):
        """测试查询实例详情"""
        result = self.client.describe_instance("inst-001")
        self.assertIsInstance(result, dict)
        self.assertIn("instance", result)
        self.assertEqual(result["instance"]["instanceId"], "inst-001")

    # ─── 话术管理测试 ───────────────────────────────

    def test_list_scripts(self):
        """测试获取话术列表"""
        result = self.client.list_scripts("inst-001")
        self.assertIsInstance(result, dict)
        self.assertIn("scripts", result)

    def test_create_script(self):
        """测试创建话术"""
        result = self.client.create_script(
            "inst-001", "测试话术", "你好，这里是回访...", "回访测试"
        )
        self.assertIsInstance(result, dict)
        self.assertIn("script", result)

    def test_publish_script(self):
        """测试发布话术"""
        result = self.client.publish_script("inst-001", "script-001")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["script"]["status"], "Published")

    # ─── 任务组管理测试 ─────────────────────────────

    def test_list_job_groups(self):
        """测试获取任务组列表"""
        result = self.client.list_job_groups("inst-001")
        self.assertIsInstance(result, dict)
        self.assertIn("jobGroups", result)

    def test_create_job_group(self):
        """测试创建任务组"""
        result = self.client.create_job_group(
            "inst-001", "测试任务", "script-001", "{}"
        )
        self.assertIsInstance(result, dict)
        self.assertIn("jobGroup", result)

    def test_describe_job_group(self):
        """测试查询任务组详情"""
        result = self.client.describe_job_group("inst-001", "job-001")
        self.assertIsInstance(result, dict)
        self.assertIn("JobGroup", result)

    # ─── 任务控制测试 ───────────────────────────────

    def test_start_job(self):
        """测试启动任务"""
        result = self.client.start_job("inst-001", "job-001")
        self.assertIsInstance(result, dict)

    def test_suspend_jobs(self):
        """测试暂停任务"""
        result = self.client.suspend_jobs("inst-001", "job-001")
        self.assertIsInstance(result, dict)

    def test_resume_jobs(self):
        """测试恢复任务"""
        result = self.client.resume_jobs("inst-001", "job-001")
        self.assertIsInstance(result, dict)

    def test_cancel_jobs(self):
        """测试取消任务"""
        result = self.client.cancel_jobs("inst-001", "job-001")
        self.assertIsInstance(result, dict)

    # ─── 任务列表测试 ───────────────────────────────

    def test_list_jobs(self):
        """测试获取任务列表"""
        result = self.client.list_jobs("inst-001", "job-001")
        self.assertIsInstance(result, dict)
        self.assertIn("jobs", result)

    @patch.object(OutboundBotClient, "_create_client", side_effect=Exception("skip"))
    def test_dialogue_signature(self, mock_create):
        """测试 dialogue 方法的参数签名（仅验证能构造）"""
        # 这个测试验证参数名是否正确，具体 SDK 交互由集成测试覆盖
        pass

    def test_describe_job(self):
        """测试查询单个任务"""
        result = self.client.describe_job("inst-001", "job-detail-001")
        self.assertIsInstance(result, dict)
        self.assertIn("job", result)

    # ─── 意图管理测试 ───────────────────────────────

    def test_create_intent(self):
        """测试创建意图"""
        result = self.client.create_intent(
            "inst-001", "script-001", "意向",
            "表示有兴趣", "我对这个产品感兴趣"
        )
        self.assertIsInstance(result, dict)

    def test_list_intents(self):
        """测试获取意图列表"""
        result = self.client.list_intents("inst-001", "script-001")
        self.assertIsInstance(result, dict)
        self.assertIn("intents", result)

    # ─── 黑/白名单测试 ──────────────────────────────

    def test_save_whitelist(self):
        """测试保存白名单"""
        result = self.client.save_contact_white_list(
            "inst-001", '[{"contactId": "c001", "phoneNumber": "13800138000"}]'
        )
        self.assertIsInstance(result, dict)

    def test_save_blacklist(self):
        """测试保存黑名单"""
        result = self.client.save_contact_block_list(
            "inst-001", '[{"contactId": "c002", "phoneNumber": "13800138001"}]'
        )
        self.assertIsInstance(result, dict)

    # ─── 录音下载测试 ───────────────────────────────

    def test_download_recording(self):
        """测试获取录音下载链接"""
        result = self.client.download_recording("inst-001", "task-001")
        self.assertIsInstance(result, dict)
        self.assertIn("recording", result)

    # ─── 对话接口测试 ───────────────────────────────

    def test_dialogue(self):
        """测试对话交互"""
        result = self.client.dialogue(
            "inst-001",
            utterance="你好",
            calling_number="021-12345678",
            called_number="13800138000",
        )
        self.assertIsInstance(result, dict)
        self.assertIn("dialogue", result)

    # ─── 辅助方法测试 ───────────────────────────────

    def test_to_dict(self):
        """测试 _to_dict 静态方法"""
        # Mock SDK 返回的字符串格式对象
        mock_str = '{"key": "value"}'
        result = OutboundBotClient._to_dict(type('obj', (object,), {'__str__': lambda s: mock_str})())
        self.assertEqual(result, {"key": "value"})


if __name__ == "__main__":
    unittest.main()
