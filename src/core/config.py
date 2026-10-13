"""Configuration management for SpeechAI.

Provides centralized configuration loaded from environment variables and .env file,
with sensible defaults and path resolution.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Automatically load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")


def _resolve_base_url() -> Optional[str]:
    """Resolve custom OpenAI Base URL from environment variables."""
    raw = (
        os.getenv("OPENAI_BASE_URL")
        or os.getenv("BASE_URL")
        or os.getenv("OPENAI_API_BASE")
        or ""
    ).strip()
    return raw if raw else None


@dataclass
class AppConfig:
    """Application configuration container."""

    # Project paths
    root_dir: Path = field(default_factory=lambda: ROOT_DIR)
    temp_dir: Path = field(default_factory=lambda: ROOT_DIR / os.getenv("TEMP_DIR", "temp"))

    # OpenAI settings
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: Optional[str] = field(default_factory=_resolve_base_url)
    chat_model: str = field(default_factory=lambda: os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"))
    openai_tts_model: str = field(default_factory=lambda: os.getenv("OPENAI_TTS_MODEL", "tts-1"))
    openai_tts_voice: str = field(default_factory=lambda: os.getenv("OPENAI_TTS_VOICE", "nova"))
    openai_whisper_model: str = field(default_factory=lambda: os.getenv("OPENAI_WHISPER_MODEL", "whisper-1"))

    # Local Whisper settings
    local_whisper_model: str = field(default_factory=lambda: os.getenv("LOCAL_WHISPER_MODEL", "tiny.en"))

    # Engine selections
    stt_engine: str = field(default_factory=lambda: os.getenv("STT_ENGINE", "openai").lower())
    tts_engine: str = field(default_factory=lambda: os.getenv("TTS_ENGINE", "openai").lower())
    playback_engine: str = field(default_factory=lambda: os.getenv("PLAYBACK_ENGINE", "auto").lower())

    # Google TTS (gTTS) settings
    gtts_language: str = field(default_factory=lambda: os.getenv("GTTS_LANGUAGE", "pt"))
    gtts_tld: str = field(default_factory=lambda: os.getenv("GTTS_TLD", "com.br"))

    # Audio recording defaults
    sample_rate: int = field(default_factory=lambda: int(os.getenv("AUDIO_SAMPLE_RATE", "44100")))
    channels: int = field(default_factory=lambda: int(os.getenv("AUDIO_CHANNELS", "1")))
    record_duration: float = field(default_factory=lambda: float(os.getenv("AUDIO_RECORD_DURATION", "5.0")))

    # Logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO").upper())

    def __post_init__(self) -> None:
        """Ensure paths and validations are initialized."""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        if self.openai_base_url is not None:
            self.openai_base_url = self.openai_base_url.strip() or None

    @property
    def has_openai_key(self) -> bool:
        """Check if an OpenAI API key is configured."""
        return bool(self.openai_api_key and self.openai_api_key.strip() and not self.openai_api_key.startswith("your_"))

    @property
    def is_openai_configured(self) -> bool:
        """Check if OpenAI service is configured (via valid API key or custom base URL)."""
        return self.has_openai_key or bool(self.openai_base_url)


# Global singleton instance
config = AppConfig()
