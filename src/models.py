"""
数据模型
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class JobGroup:
    """任务组"""
    job_group_id: str
    job_group_name: str
    script_id: str
    script_name: str
    strategy_json: str
    total_jobs: int = 0
    total_completed: int = 0
    total_pending: int = 0
    status: str = ""
    creation_time: str = ""


@dataclass
class Job:
    """单个外呼任务"""
    job_id: str
    job_group_id: str
    calling_number: str
    called_number: str
    status: str = ""
    duration: int = 0
    callee_name: str = ""
    script_content: str = ""
    end_reason: str = ""
    contact_id: str = ""


@dataclass
class Script:
    """话术"""
    script_id: str
    script_name: str
    script_content: str = ""
    script_description: str = ""
    status: str = ""
    is_debugged: bool = False
    is_published: bool = False
    update_time: str = ""


@dataclass
class Intent:
    """意图"""
    intent_id: str
    intent_name: str
    intent_description: str = ""
    utterances: str = ""
    create_time: str = ""


@dataclass
class Contact:
    """联系人"""
    phone_number: str
    name: str = ""
    contact_id: str = ""
