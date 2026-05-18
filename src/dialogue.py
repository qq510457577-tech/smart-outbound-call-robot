"""
对话管理器 - 实时对话交互、意图识别
"""
import logging
from typing import Dict, Optional

from .client import OutboundBotClient
from .config import settings

logger = logging.getLogger(__name__)


class DialogueManager:
    """对话交互管理器"""

    def __init__(self, client: Optional[OutboundBotClient] = None):
        self.client = client or OutboundBotClient()

    def send_utterance(
        self,
        session_id: str,
        utterance: str,
        calling_number: str,
        called_number: str,
    ) -> Dict:
        """
        发送用户 utterance 并获取回复

        Args:
            session_id: 会话ID
            utterance: 用户说的话语
            calling_number: 主叫号码
            called_number: 被叫号码

        Returns:
            AI 回复内容
        """
        result = self.client.dialogue(
            instance_id=settings.INSTANCE_ID,
            session_id=session_id,
            utterance=utterance,
            calling_number=calling_number,
            called_number=called_number,
        )
        return result

    def analyze_intent(self, text: str) -> str:
        """
        分析用户意图（基于意图关键词匹配）

        实际项目中可对接阿里云 Beebot 意图识别
        """
        # 简单规则示例
        intent_map = {
            "意向": "INTERESTED",
            "考虑": "CONSIDERING",
            "不需要": "NOT_INTERESTED",
            "别打了": "REJECTED",
            "稍后": "CALL_BACK",
            "没时间": "CALL_BACK",
            "好的": "AGREED",
            "同意": "AGREED",
        }

        for keyword, intent in intent_map.items():
            if keyword in text:
                return intent
        return "UNKNOWN"
