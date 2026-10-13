"""Text-to-Speech (TTS) module initialization."""

from src.core.tts.synthesizer import (
    synthesize_text,
    synthesize_with_openai,
    synthesize_with_gtts,
    synthesize_to_bytes,
)
from src.core.tts.chatgpt_tts_handler import (
    ChatGPTTTSHandler,
    chat_and_speak,
    get_chatgpt_response,
    generate_audio_file,
    default_handler,
)

__all__ = [
    "synthesize_text",
    "synthesize_with_openai",
    "synthesize_with_gtts",
    "synthesize_to_bytes",
    "ChatGPTTTSHandler",
    "chat_and_speak",
    "get_chatgpt_response",
    "generate_audio_file",
    "default_handler",
]