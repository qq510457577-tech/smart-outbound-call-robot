"""
DialogueManager 单元测试
"""
import unittest

from src.dialogue import DialogueManager


class MockClient:
    """模拟 OutboundBotClient"""

    def dialogue(self, instance_id, session_id, utterance, calling_number, called_number):
        return {
            "dialogue": {
                "intent": "INTENT_OK",
                "response": "好的，我了解了",
                "turns": 3,
            }
        }


class TestDialogueManager(unittest.TestCase):
    """DialogueManager 测试类"""

    def setUp(self):
        self.client = MockClient()
        self.manager = DialogueManager(self.client)

    def test_send_utterance(self):
        """测试发送 utterance"""
        result = self.manager.send_utterance(
            session_id="session-001",
            utterance="你好，请问是张先生吗？",
            calling_number="021-12345678",
            called_number="13800138000",
        )
        self.assertIsInstance(result, dict)
        self.assertIn("dialogue", result)
        self.assertEqual(result["dialogue"]["intent"], "INTENT_OK")

    def test_analyze_intent_focused(self):
        """测试意图分析 - 明确意向"""
        intent = self.manager.analyze_intent("我很有意向，请尽快联系我")
        self.assertEqual(intent, "INTERESTED")

    def test_analyze_intent_considering(self):
        """测试意图分析 - 需要考虑"""
        intent = self.manager.analyze_intent("我需要考虑一下")
        self.assertEqual(intent, "CONSIDERING")

    def test_analyze_intent_rejected(self):
        """测试意图分析 - 拒绝"""
        intent = self.manager.analyze_intent("别打了，不需要")
        self.assertEqual(intent, "REJECTED")

    def test_analyze_intent_callback(self):
        """测试意图分析 - 稍后联系"""
        intent = self.manager.analyze_intent("我最近没时间，下周再打吧")
        self.assertIn(intent, ["CALL_BACK"])

    def test_analyze_intent_agreed(self):
        """测试意图分析 - 同意"""
        intent = self.manager.analyze_intent("好的，我同意")
        self.assertEqual(intent, "AGREED")

    def test_analyze_intent_unknown(self):
        """测试意图分析 - 未知意图"""
        intent = self.manager.analyze_intent("今天天气不错啊")
        self.assertEqual(intent, "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
