"""
批量外呼示例 - 大数据量分批创建
"""
import json
import csv
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.task_manager import TaskManager
from src.config import settings


def load_contacts_from_csv(filepath: str) -> list:
    """从 CSV 文件加载联系人"""
    contacts = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append({
                "phone": row.get("phone", "").strip(),
                "name": row.get("name", "").strip(),
            })
    return contacts


def main():
    manager = TaskManager()

    # CSV 格式: phone,name
    # 13800138001,张三
    # 13800138002,李四
    contacts = load_contacts_from_csv("contacts.csv")

    # 每批 100 条分批次创建
    batch_size = 100
    script_id = "your_script_id"

    for i in range(0, len(contacts), batch_size):
        batch = contacts[i : i + batch_size]
        job_group_id = manager.create_batch_job(
            name=f"批量外呼-第{i//batch_size + 1}批",
            script_id=script_id,
            contacts=batch,
        )
        print(f"批次 {i//batch_size + 1}: {job_group_id}")
        manager.start(job_group_id)


if __name__ == "__main__":
    if not os.path.exists("contacts.csv"):
        print("请先准备 contacts.csv 文件")
        sys.exit(1)
    main()
