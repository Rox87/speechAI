"""Backwards compatibility alias for tts_core.

Re-exports core functionality from `chatgpt_tts_handler`.
"""

from src.core.tts.chatgpt_tts_handler import (
    ChatGPTTTSHandler,
    chat_and_speak,
    get_chatgpt_response,
    generate_audio_file,
    default_handler,
)

__all__ = [
    "ChatGPTTTSHandler",
    "chat_and_speak",
    "get_chatgpt_response",
    "generate_audio_file",
    "default_handler",
]

if __name__ == "__main__":
    chat_and_speak("Hello from TTS Core!")
