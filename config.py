import os
from pathlib import Path

from dotenv import load_dotenv

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Application configuration."""

    APP_NAME: str = os.getenv(
        "APP_NAME",
        "ComicCraft - AI Comic Story Creator",
    )

    GEMINI_API_KEY: str = os.getenv(
        "GEMINI_API_KEY",
        "",
    )

    # Text-generation models.
    # These can be changed without modifying application code.
    GEMINI_FLASH_MODEL: str = os.getenv(
        "GEMINI_FLASH_MODEL",
        "gemini-3.8-flash",
    )

    GEMINI_PRO_MODEL: str = os.getenv(
        "GEMINI_PRO_MODEL",
        "gemini-3.8-flash",
    )

    # Gemini image model.
    GEMINI_IMAGE_MODEL: str = os.getenv(
        "GEMINI_IMAGE_MODEL",
        "gemini-3.1-flash-image",
    )

    IMAGE_PROVIDER: str = os.getenv(
        "IMAGE_PROVIDER",
        "gemini",
    ).lower()

    HF_API_KEY: str = os.getenv(
        "HF_API_KEY",
        "",
    )

    STABLE_DIFFUSION_MODEL: str = os.getenv(
        "STABLE_DIFFUSION_MODEL",
        "runwayml/stable-diffusion-v1-5",
    )

    DEBUG: bool = os.getenv(
        "DEBUG",
        "true",
    ).lower() == "true"

    HOST: str = os.getenv(
        "HOST",
        "127.0.0.1",
    )

    PORT: int = int(
        os.getenv(
            "PORT",
            "8000",
        )
    )

    PANEL_COUNT: int = int(
        os.getenv(
            "PANEL_COUNT",
            "5",
        )
    )

    STATIC_DIR: Path = BASE_DIR / "static"
    PANEL_DIR: Path = STATIC_DIR / "panels"
    EXPORT_DIR: Path = STATIC_DIR / "exports"
    TEMPLATE_DIR: Path = BASE_DIR / "templates"

    def create_directories(self) -> None:
        """Create folders required by ComicCraft."""
        self.STATIC_DIR.mkdir(parents=True, exist_ok=True)
        self.PANEL_DIR.mkdir(parents=True, exist_ok=True)
        self.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        self.TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.create_directories()