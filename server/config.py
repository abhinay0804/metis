"""
Application configuration loaded from environment variables.
"""
import os


class _Settings:
    """Central configuration — reads from env vars with sensible defaults."""

    def __init__(self):
        # Database
        self.SQLITE_FALLBACK = os.environ.get("SQLITE_FALLBACK", "0") == "1"
        if self.SQLITE_FALLBACK:
            self.DATABASE_URL = os.environ.get(
                "DATABASE_URL", "sqlite+aiosqlite:///./metis.db"
            )
        else:
            self.DATABASE_URL = os.environ.get(
                "DATABASE_URL",
                "postgresql+asyncpg://metis:metis@localhost:5432/metis",
            )

        # JWT & Auth
        self.JWT_SECRET_KEY = os.environ.get(
            "JWT_SECRET_KEY", "change-me-in-production"
        )
        self.JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
        )
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(
            os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7")
        )

        # Redis
        self.REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

        # ML Models
        self.YOLO_MODEL_PATH = os.environ.get("YOLO_MODEL_PATH", "runs/detect/ml/models/logo_detection/weights/best.pt")


# Singleton instance — import as `from server.config import settings`
settings = _Settings()
