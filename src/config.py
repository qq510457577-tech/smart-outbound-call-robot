import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # 阿里云认证
    ACCESS_KEY_ID: str = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID", "")
    ACCESS_KEY_SECRET: str = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET", "")
    REGION_ID: str = os.getenv("ALIBABA_CLOUD_REGION_ID", "cn-shanghai")

    # 外呼机器人实例
    INSTANCE_ID: str = os.getenv("OUTBOUNDBOT_INSTANCE_ID", "")

    # 外呼默认配置
    DEFAULT_CONCURRENCY: int = int(os.getenv("DEFAULT_CONCURRENCY", "5"))
    MAX_RETRY_TIMES: int = int(os.getenv("MAX_RETRY_TIMES", "3"))
    CALL_TIMEOUT_SECONDS: int = int(os.getenv("CALL_TIMEOUT_SECONDS", "60"))


settings = Settings()
