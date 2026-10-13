"""Backwards compatibility alias for text_to_speech.

Re-exports core functionality from `chatgpt_tts_handler` and `synthesizer`.
"""

from src.core.tts.chatgpt_tts_handler import (
    ChatGPTTTSHandler,
    chat_and_speak,
    get_chatgpt_response,
    generate_audio_file,
    default_handler,
)
from src.core.tts.synthesizer import (
    synthesize_text,
    synthesize_with_openai,
    synthesize_with_gtts,
    synthesize_to_bytes,
)

__all__ = [
    "ChatGPTTTSHandler",
    "chat_and_speak",
    "get_chatgpt_response",
    "generate_audio_file",
    "default_handler",
    "synthesize_text",
    "synthesize_with_openai",
    "synthesize_with_gtts",
    "synthesize_to_bytes",
]

if __name__ == "__main__":
    chat_and_speak("Hello from Text to Speech!")
