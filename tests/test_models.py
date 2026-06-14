"""
数据模型 单元测试
"""
import unittest
from src.models import JobGroup, Job, Script, Intent, Contact


class TestModels(unittest.TestCase):
    """数据模型测试类"""

    def test_job_group(self):
        """测试 JobGroup 数据类"""
        group = JobGroup(
            job_group_id="jg-001",
            job_group_name="回访任务",
            script_id="script-001",
            script_name="回访话术",
            strategy_json='{"type": "Fixed"}',
        )
        self.assertEqual(group.job_group_id, "jg-001")
        self.assertEqual(group.total_jobs, 0)
        self.assertEqual(group.status, "")

    def test_job(self):
        """测试 Job 数据类"""
        job = Job(
            job_id="job-001",
            job_group_id="jg-001",
            calling_number="021-12345678",
            called_number="13800138000",
        )
        self.assertEqual(job.job_id, "job-001")
        self.assertEqual(job.duration, 0)
        self.assertEqual(job.status, "")

    def test_script(self):
        """测试 Script 数据类"""
        script = Script(
            script_id="script-001",
            script_name="回访话术",
            script_content="你好，这里是回访...",
        )
        self.assertEqual(script.script_id, "script-001")
        self.assertFalse(script.is_published)

    def test_intent(self):
        """测试 Intent 数据类"""
        intent = Intent(
            intent_id="intent-001",
            intent_name="意向",
            utterances='["我感兴趣", "我要购买"]',
        )
        self.assertEqual(intent.intent_name, "意向")

    def test_contact(self):
        """测试 Contact 数据类"""
        contact = Contact(
            phone_number="13800138000",
            name="张三",
        )
        self.assertEqual(contact.phone_number, "13800138000")
        self.assertEqual(contact.name, "张三")


if __name__ == "__main__":
    unittest.main()
