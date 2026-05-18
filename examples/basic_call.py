"""
基础外呼示例 - 创建并启动一个简单的外呼任务
"""
import json
import logging
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.client import OutboundBotClient
from src.task_manager import TaskManager
from src.config import settings

logging.basicConfig(level=logging.INFO)


def main():
    client = OutboundBotClient()
    manager = TaskManager(client)

    # 0. 列出已存在的话术
    print("=== 已有话术 ===")
    scripts = client.list_scripts(settings.INSTANCE_ID)
    for s in scripts:
        print(f"  [{s.get('ScriptId','?')}] {s.get('ScriptName','?')}")

    # 1. 创建任务
    script_id = input("请输入话术ID: ").strip()

    contacts = [
        {"phone": "13800138001", "name": "张三"},
        {"phone": "13800138002", "name": "李四"},
    ]

    job_group_id = manager.create_batch_job(
        name="回访测试-1",
        script_id=script_id,
        contacts=contacts,
        description="测试批量外呼",
    )
    print(f"\n创建任务组成功: {job_group_id}")

    # 2. 启动任务
    if manager.start(job_group_id):
        print("任务已启动")

    # 3. 查询进度
    progress = manager.get_progress(job_group_id)
    print(f"任务进度: {json.dumps(progress, ensure_ascii=False, indent=2)}")


if __name__ == "__main__":
    main()
