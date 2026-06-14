"""
阿里云 Outbound Bot SDK 封装
"""
import json
import logging
from typing import Optional, List, Dict, Any

from alibabacloud_outboundbot20191226.client import Client as OutboundBotClientSDK
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_outboundbot20191226 import models as outbound_models

from .config import settings

logger = logging.getLogger(__name__)


class OutboundBotClient:
    """阿里云智能外呼机器人客户端封装"""

    def __init__(self):
        self._client = self._create_client()

    def _create_client(self) -> OutboundBotClientSDK:
        config = open_api_models.Config(
            access_key_id=settings.ACCESS_KEY_ID,
            access_key_secret=settings.ACCESS_KEY_SECRET,
            region_id=settings.REGION_ID,
        )
        config.endpoint = f"outboundbot.{settings.REGION_ID}.aliyuncs.com"
        return OutboundBotClientSDK(config)

    # ─── 实例管理 ─────────────────────────────────

    def list_instances(self) -> List[Dict]:
        """获取外呼机器人实例列表"""
        req = outbound_models.ListInstancesRequest()
        resp = self._client.list_instances(req)
        return self._to_dict(resp.body)

    def describe_instance(self, instance_id: str) -> Dict:
        """查询实例详情"""
        req = outbound_models.DescribeInstanceRequest(instance_id=instance_id)
        resp = self._client.describe_instance(req)
        return self._to_dict(resp.body)

    # ─── 话术管理 ─────────────────────────────────

    def list_scripts(self, instance_id: str) -> List[Dict]:
        """获取话术列表"""
        req = outbound_models.ListScriptsRequest(instance_id=instance_id)
        resp = self._client.list_scripts(req)
        return self._to_dict(resp.body)

    def create_script(
        self, instance_id: str, name: str,
        script_content: str, script_description: str = ""
    ) -> Dict:
        """创建话术"""
        req = outbound_models.CreateScriptRequest(
            instance_id=instance_id,
            script_name=name,
            script_content=script_content,
            script_description=script_description,
        )
        resp = self._client.create_script(req)
        return self._to_dict(resp.body)

    def describe_script(self, instance_id: str, script_id: str) -> Dict:
        """查询话术详情"""
        req = outbound_models.DescribeScriptRequest(
            instance_id=instance_id, script_id=script_id
        )
        resp = self._client.describe_script(req)
        return self._to_dict(resp.body)

    def publish_script(self, instance_id: str, script_id: str) -> Dict:
        """发布话术"""
        req = outbound_models.PublishScriptRequest(
            instance_id=instance_id, script_id=script_id
        )
        resp = self._client.publish_script(req)
        return self._to_dict(resp.body)

    # ─── 任务管理 ─────────────────────────────────

    def list_job_groups(self, instance_id: str) -> List[Dict]:
        """获取任务组列表"""
        req = outbound_models.ListJobGroupsRequest(instance_id=instance_id)
        resp = self._client.list_job_groups(req)
        return self._to_dict(resp.body)

    def create_job_group(
        self, instance_id: str, name: str,
        script_id: str, strategy_json: str,
        description: str = "",
        recall_strategy_json: str = None,
    ) -> Dict:
        """创建任务组"""
        req = outbound_models.CreateJobGroupRequest(
            instance_id=instance_id,
            job_group_name=name,
            script_id=script_id,
            strategy_json=strategy_json,
            job_group_description=description,
            recall_strategy_json=recall_strategy_json,
        )
        resp = self._client.create_job_group(req)
        return self._to_dict(resp.body)

    def describe_job_group(self, instance_id: str, job_group_id: str) -> Dict:
        """查询任务组详情"""
        req = outbound_models.DescribeJobGroupRequest(
            instance_id=instance_id, job_group_id=job_group_id
        )
        resp = self._client.describe_job_group(req)
        return self._to_dict(resp.body)

    def start_job(self, instance_id: str, job_group_id: str) -> Dict:
        """启动任务"""
        req = outbound_models.StartJobRequest(
            instance_id=instance_id, job_group_id=job_group_id
        )
        resp = self._client.start_job(req)
        return self._to_dict(resp.body)

    def suspend_jobs(self, instance_id: str, job_group_id: str) -> Dict:
        """暂停任务"""
        req = outbound_models.SuspendJobsRequest(
            instance_id=instance_id, job_group_id=job_group_id
        )
        resp = self._client.suspend_jobs(req)
        return self._to_dict(resp.body)

    def resume_jobs(self, instance_id: str, job_group_id: str) -> Dict:
        """恢复任务"""
        req = outbound_models.ResumeJobsRequest(
            instance_id=instance_id, job_group_id=job_group_id
        )
        resp = self._client.resume_jobs(req)
        return self._to_dict(resp.body)

    def cancel_jobs(self, instance_id: str, job_group_id: str) -> Dict:
        """取消任务"""
        req = outbound_models.CancelJobsRequest(
            instance_id=instance_id, job_group_id=job_group_id
        )
        resp = self._client.cancel_jobs(req)
        return self._to_dict(resp.body)

    def list_jobs(self, instance_id: str, job_group_id: str) -> List[Dict]:
        """获取任务列表

        注意: 阿里云 SDK ListJobsRequest 使用 job_id (单个任务ID)
        如果要获取任务组下的所有任务, 建议通过 describe_job_group 的
        Progress 信息或外部逻辑追踪。
        """
        req = outbound_models.ListJobsRequest(
            instance_id=instance_id, job_id=job_group_id
        )
        resp = self._client.list_jobs(req)
        return self._to_dict(resp.body)

    def describe_job(self, instance_id: str, job_id: str) -> Dict:
        """查询单个任务"""
        req = outbound_models.DescribeJobRequest(
            instance_id=instance_id, job_id=job_id
        )
        resp = self._client.describe_job(req)
        return self._to_dict(resp.body)

    def assign_jobs(
        self, instance_id: str, job_group_id: str,
        calling_numbers: List[str], jobs_json: str
    ) -> Dict:
        """分配外呼任务（指定号码）"""
        req = outbound_models.AssignJobsRequest(
            instance_id=instance_id,
            job_group_id=job_group_id,
            calling_numbers=calling_numbers,
            jobs_json=jobs_json,
        )
        resp = self._client.assign_jobs(req)
        return self._to_dict(resp.body)

    # ─── 意图管理 ─────────────────────────────────

    def create_intent(
        self, instance_id: str, script_id: str,
        intent_name: str, intent_description: str = "",
        utterances: str = None,
    ) -> Dict:
        """创建意图"""
        req = outbound_models.CreateIntentRequest(
            instance_id=instance_id,
            script_id=script_id,
            intent_name=intent_name,
            intent_description=intent_description,
            utterances=utterances,
        )
        resp = self._client.create_intent(req)
        return self._to_dict(resp.body)

    def list_intents(self, instance_id: str, script_id: str) -> List[Dict]:
        """获取意图列表"""
        req = outbound_models.ListIntentsRequest(
            instance_id=instance_id, script_id=script_id
        )
        resp = self._client.list_intents(req)
        return self._to_dict(resp.body)

    # ─── 黑/白名单 ────────────────────────────────

    def save_contact_white_list(
        self, instance_id: str, contact_list: str
    ) -> Dict:
        """保存白名单

        Args:
            instance_id: 实例ID
            contact_list: JSON 格式的联系人列表字符串
        """
        req = outbound_models.SaveContactWhiteListRequest(
            instance_id=instance_id,
            contact_white_lists_json=contact_list,
        )
        resp = self._client.save_contact_white_list(req)
        return self._to_dict(resp.body)

    def save_contact_block_list(
        self, instance_id: str, contact_list: str
    ) -> Dict:
        """保存黑名单

        Args:
            instance_id: 实例ID
            contact_list: JSON 格式的联系人列表字符串
        """
        req = outbound_models.SaveContactBlockListRequest(
            instance_id=instance_id,
            contact_block_lists_json=contact_list,
        )
        resp = self._client.save_contact_block_list(req)
        return self._to_dict(resp.body)

    # ─── 录音下载 ─────────────────────────────────

    def download_recording(
        self, instance_id: str, task_id: str,
        need_voice_slice_recording: bool = False,
        swap_channels: bool = False,
    ) -> Dict:
        """获取录音下载链接

        Args:
            instance_id: 实例ID
            task_id: 通话任务ID (非 job_id)
            need_voice_slice_recording: 是否需要语音切片录音
            swap_channels: 是否交换通道
        """
        req = outbound_models.DownloadRecordingRequest(
            instance_id=instance_id,
            task_id=task_id,
            need_voice_slice_recording=need_voice_slice_recording,
            swap_channels=swap_channels,
        )
        resp = self._client.download_recording(req)
        return self._to_dict(resp.body)

    # ─── 通话对话接口 ─────────────────────────────

    def dialogue(
        self, instance_id: str, utterance: str,
        calling_number: str, called_number: str,
        task_id: str = "", call_id: str = "",
        script_id: str = "", scenario_id: str = "",
    ) -> Dict:
        """对话交互（实时对话接口）

        Args:
            instance_id: 实例ID
            utterance: 用户说的话语
            calling_number: 主叫号码
            called_number: 被叫号码
            task_id: 通话任务ID
            call_id: 通话ID
            script_id: 话术ID
            scenario_id: 场景ID
        """
        req = outbound_models.DialogueRequest(
            instance_id=instance_id,
            utterance=utterance,
            calling_number=calling_number,
            called_number=called_number,
            task_id=task_id,
            call_id=call_id,
            script_id=script_id,
            scenario_id=scenario_id,
        )
        resp = self._client.dialogue(req)
        return self._to_dict(resp.body)

    # ─── 辅助方法 ─────────────────────────────────

    @staticmethod
    def _to_dict(obj) -> Any:
        """SDK 返回对象转字典"""
        return json.loads(str(obj))
