from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "公路工程质检文控 Demo"
    secret_key: str = "qms-demo-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12
    database_url: str = f"sqlite:///{BASE_DIR / 'qms.db'}"
    upload_dir: Path = BASE_DIR / "uploads"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
