"""Core components for SpeechAI."""

from src.core.config import config, AppConfig
from src.core.logger import logger, get_logger
from src.core.voice_assistant import VoiceAssistant, assistant, chat_and_speak, listen_and_respond
from src.core.audio import (
    AudioPlayer,
    player,
    play_audio,
    record_audio_to_bytes,
    record_audio_to_file,
    transcribe_audio,
)
from src.core.tts import (
    synthesize_text,
    synthesize_with_openai,
    synthesize_with_gtts,
    synthesize_to_bytes,
    ChatGPTTTSHandler,
)
from src.core.utils import clean_folder, clean_temp_dir

__all__ = [
    "config",
    "AppConfig",
    "logger",
    "get_logger",
    "VoiceAssistant",
    "assistant",
    "chat_and_speak",
    "listen_and_respond",
    "AudioPlayer",
    "player",
    "play_audio",
    "record_audio_to_bytes",
    "record_audio_to_file",
    "transcribe_audio",
    "synthesize_text",
    "synthesize_with_openai",
    "synthesize_with_gtts",
    "synthesize_to_bytes",
    "ChatGPTTTSHandler",
    "clean_folder",
    "clean_temp_dir",
]