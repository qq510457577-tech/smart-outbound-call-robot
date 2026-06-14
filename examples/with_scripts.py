"""
话术管理示例 - 创建、发布、管理话术
"""
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client import OutboundBotClient
from src.config import settings

logging.basicConfig(level=logging.INFO)


def main():
    client = OutboundBotClient()
    instance_id = settings.INSTANCE_ID

    # 0. 查看现有话术
    print("=== 现有话术列表 ===")
    scripts = client.list_scripts(instance_id)
    for s in scripts.get("scripts", []):
        print(f"  [{s.get('scriptId', '?')}] {s.get('scriptName', '?')}")
        print(f"    状态: {s.get('status', '?')} | 更新时间: {s.get('updateTime', '?')}")
    print()

    # 1. 创建新话术
    script_content = """
    {
        "type": "flow",
        "nodes": [
            {
                "id": "start",
                "type": "start",
                "text": "您好，这里是XX公司回访专员，请问您方便接听吗？",
                "next": "waiting_response"
            },
            {
                "id": "waiting_response",
                "type": "intent",
                "intents": ["AGREED", "REJECTED", "NOT_INTERESTED"],
                "outcomes": {
                    "AGREED": "ask_topic",
                    "REJECTED": "end_reject",
                    "NOT_INTERESTED": "end_reject"
                }
            },
            {
                "id": "ask_topic",
                "type": "text",
                "text": "感谢您的接听。想了解一下您对之前购买的产品还满意吗？"
            }
        ]
    }
    """

    print("=== 创建新话术 ===")
    result = client.create_script(
        instance_id=instance_id,
        name="客户回访-v2",
        script_content=script_content,
        script_description="2024年Q2版本客户回访话术",
    )
    script_id = result.get("script", {}).get("scriptId", "")
    print(f"创建成功: script_id = {script_id}")

    # 2. 查询话术详情
    print("\n=== 话术详情 ===")
    detail = client.describe_script(instance_id, script_id)
    print(json.dumps(detail, ensure_ascii=False, indent=2))

    # 3. 发布话术（使其可用于外呼任务）
    print(f"\n=== 发布话术 {script_id} ===")
    publish_result = client.publish_script(instance_id, script_id)
    print(json.dumps(publish_result, ensure_ascii=False, indent=2))

    # 4. 查看发布后的话术列表
    print("\n=== 发布后话术列表 ===")
    scripts = client.list_scripts(instance_id)
    for s in scripts.get("scripts", []):
        status = s.get("status", "")
        published = "✓已发布" if status == "Published" else "✗未发布"
        print(f"  [{s.get('scriptId', '?')}] {s.get('scriptName', '?')}  {published}")

    # 5. 管理意图
    print("\n=== 创建意图 ===")
    intent_result = client.create_intent(
        instance_id=instance_id,
        script_id=script_id,
        intent_name="回访意向",
        intent_description="客户对产品回访的回应意向",
        utterances='["我很满意", "还不错", "挺好的", "比较满意"]',
    )
    intent_id = intent_result.get("intent", {}).get("intentId", "")
    print(f"意图创建成功: intent_id = {intent_id}")

    # 6. 查看意图列表
    print("\n=== 意图列表 ===")
    intents = client.list_intents(instance_id, script_id)
    for intent in intents.get("intents", []):
        print(f"  [{intent.get('intentId', '?')}] {intent.get('intentName', '?')}: {intent.get('utterances', '')}")


if __name__ == "__main__":
    main()
