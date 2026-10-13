"""Audio transcription module supporting both OpenAI Whisper API and local faster-whisper."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Generator, Optional, Union, Any

from src.core.logger import logger
from src.core.config import config
from src.core.client import get_openai_client


# Cached local whisper model instance (lazy loaded)
_local_whisper_model = None


def get_local_whisper_model():
    """Lazily load faster-whisper model only when requested."""
    global _local_whisper_model
    if _local_whisper_model is None:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            raise ImportError(
                "faster-whisper is not installed. Install it with: pip install faster-whisper"
            )
        logger.info(f"Loading local Whisper model: {config.local_whisper_model} on CPU...")
        _local_whisper_model = WhisperModel(
            config.local_whisper_model,
            device="cpu",
            compute_type="int8"
        )
    return _local_whisper_model


def transcribe_with_openai(
    audio_source: Union[str, Path, io.BytesIO, bytes],
    model: Optional[str] = None,
    language: Optional[str] = None,
) -> str:
    """Transcribe audio using OpenAI Whisper API.

    Args:
        audio_source: File path, BytesIO buffer, or raw bytes.
        model: Whisper model name (default: whisper-1).
        language: Optional ISO 639-1 language code (e.g. 'en', 'pt').

    Returns:
        str: Transcribed text.
    """
    client = get_openai_client()
    model_name = model or config.openai_whisper_model
    kwargs: Dict[str, Any] = {"model": model_name}
    target_lang = language or config.whisper_language
    if target_lang:
        kwargs["language"] = "pt" if target_lang.lower() in ("pt", "pt-br", "pt_br") else target_lang

    if isinstance(audio_source, (str, Path)):
        path = Path(audio_source)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")
        with open(path, "rb") as f:
            kwargs["file"] = f
            response = client.audio.transcriptions.create(**kwargs)
            return response.text.strip()
    elif isinstance(audio_source, io.BytesIO):
        audio_source.seek(0)
        file_payload = ("audio.wav", audio_source.read(), "audio/wav")
    elif isinstance(audio_source, bytes):
        file_payload = ("audio.wav", audio_source, "audio/wav")
    else:
        raise TypeError(f"Unsupported audio source type: {type(audio_source)}")

    kwargs["file"] = file_payload
    response = client.audio.transcriptions.create(**kwargs)
    return response.text.strip()


def transcribe_with_local_whisper(
    audio_source: Union[str, Path, io.BytesIO],
    language: Optional[str] = None,
) -> Generator[str, None, None]:
    """Transcribe audio using local faster-whisper, yielding segment texts.

    Args:
        audio_source: File path or BytesIO buffer.
        language: Language code for transcription. Defaults to config.whisper_language.

    Yields:
        str: Segment text transcription.
    """
    model = get_local_whisper_model()

    input_data: Any
    if isinstance(audio_source, io.BytesIO):
        audio_source.seek(0)
        input_data = audio_source
    else:
        input_data = str(audio_source)

    target_lang = language or config.whisper_language
    kwargs: Dict[str, Any] = {}
    if target_lang and not config.local_whisper_model.endswith(".en"):
        kwargs["language"] = "pt" if target_lang.lower() in ("pt", "pt-br", "pt_br") else target_lang

    segments, _ = model.transcribe(input_data, **kwargs)
    for segment in segments:
        yield segment.text


def transcribe_audio(
    audio_source: Union[str, Path, io.BytesIO, bytes],
    engine: Optional[str] = None,
    language: Optional[str] = None,
) -> str:
    """High-level unified audio transcription function.

    Args:
        audio_source: Audio file path or BytesIO buffer.
        engine: 'openai' or 'local'. Defaults to config.stt_engine.
        language: Optional language code. Defaults to config.whisper_language.

    Returns:
        str: Complete transcribed text.
    """
    selected_engine = (engine or config.stt_engine).lower()

    if selected_engine == "local":
        try:
            segments = list(transcribe_with_local_whisper(audio_source, language=language))
            return " ".join(s.strip() for s in segments if s.strip())
        except ImportError as e:
            logger.warning(f"Local Whisper unavailable ({e}), falling back to OpenAI Whisper API.")

    # Default to OpenAI
    return transcribe_with_openai(audio_source, language=language)


# Backwards compatibility wrappers
def openai_whisper_api(audio_file: Union[str, Path]) -> str:
    """Backwards compatible wrapper for OpenAI Whisper API transcription."""
    return transcribe_with_openai(audio_file)


def local_transcribe_audio(file_path: Union[str, Path, io.BytesIO]) -> Generator[str, None, None]:
    """Backwards compatible wrapper for local transcription."""
    if config.stt_engine == "local":
        try:
            yield from transcribe_with_local_whisper(file_path)
            return
        except ImportError:
            logger.warning("faster-whisper not installed; falling back to OpenAI Whisper API.")

    # Fallback to OpenAI API
    text = transcribe_with_openai(file_path)
    if text:
        yield text
