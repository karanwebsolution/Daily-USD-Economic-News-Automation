import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Config:
    SARVAM_API_KEY: str = os.getenv("SARVAM_API_KEY", "")
    SARVAM_BASE_URL: str = "https://api.sarvam.ai/v1"
    SARVAM_MODEL: str = "sarvam-105b"  # or sarvam-30b as available

    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    RECIPIENT_EMAIL: str = os.getenv("RECIPIENT_EMAIL", "")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        required = [
            ("SARVAM_API_KEY", cls.SARVAM_API_KEY),
            ("SMTP_EMAIL", cls.SMTP_EMAIL),
            ("SMTP_PASSWORD", cls.SMTP_PASSWORD),
            ("RECIPIENT_EMAIL", cls.RECIPIENT_EMAIL),
        ]
        missing = [name for name, val in required if not val]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

config = Config()