"""Audio processing, playback, recording, and transcription module."""

from src.core.audio.player import (
    AudioPlayer,
    player,
    play_audio,
    play_with_pygame,
    play_with_playsound,
)
from src.core.audio.recorder import (
    check_audio_input_device,
    record_audio_to_bytes,
    record_audio_to_file,
    audio_stream_generator,
)
from src.core.audio.audio_transcriber import (
    transcribe_audio,
    transcribe_with_openai,
    transcribe_with_local_whisper,
    openai_whisper_api,
    local_transcribe_audio,
)

__all__ = [
    "AudioPlayer",
    "player",
    "play_audio",
    "play_with_pygame",
    "play_with_playsound",
    "check_audio_input_device",
    "record_audio_to_bytes",
    "record_audio_to_file",
    "audio_stream_generator",
    "transcribe_audio",
    "transcribe_with_openai",
    "transcribe_with_local_whisper",
    "openai_whisper_api",
    "local_transcribe_audio",
]