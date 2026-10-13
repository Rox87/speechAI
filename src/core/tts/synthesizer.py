"""Text-to-speech synthesis functionality supporting OpenAI TTS and Google TTS (gTTS)."""

from __future__ import annotations

import io
import time
from pathlib import Path
from typing import Optional, Union

from src.core.logger import logger
from src.core.config import config
from src.core.client import get_openai_client


def synthesize_with_openai(
    text: str,
    output_file: Optional[Union[str, Path]] = None,
    voice: Optional[str] = None,
    model: Optional[str] = None,
) -> Optional[Path]:
    """Synthesize text to speech using OpenAI TTS.

    Args:
        text: Text to speak.
        output_file: Target file path. If None, generated automatically in temp_dir.
        voice: Voice choice (nova, alloy, echo, fable, onyx, shimmer).
        model: TTS model (tts-1 or tts-1-hd).

    Returns:
        Optional[Path]: Path to generated MP3 file, or None if synthesis failed.
    """
    if not config.has_openai_key:
        logger.error("Cannot synthesize with OpenAI: OPENAI_API_KEY is not configured.")
        return None

    voice_name = voice or config.openai_tts_voice
    model_name = model or config.openai_tts_model

    # If OpenRouter is configured and model is openai/tts-1 or tts-1, map to supported OpenRouter model
    if config.openai_base_url and "openrouter.ai" in config.openai_base_url.lower():
        if model_name in ("openai/tts-1", "tts-1", "tts-1-hd"):
            model_name = "hexgrad/kokoro-82m"
            if voice_name in ("nova", "alloy", "echo", "fable", "onyx", "shimmer"):
                voice_name = "af_bella"
            logger.info(f"OpenRouter detectado: mapeando TTS para {model_name} (voz: {voice_name})")

    if output_file is None:
        target_path = config.temp_dir / f"tts_openai_{int(time.time() * 1000)}.mp3"
    else:
        target_path = Path(output_file)

    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        client = get_openai_client()
        logger.debug(f"Synthesizing {len(text)} chars with OpenAI TTS ({model_name}, {voice_name})...")

        response = client.audio.speech.create(
            model=model_name,
            voice=voice_name,
            input=text,
        )

        # Use modern write_to_file or write bytes directly
        if hasattr(response, "write_to_file"):
            response.write_to_file(target_path)
        else:
            with open(target_path, "wb") as f:
                f.write(response.content)

        logger.debug(f"OpenAI TTS saved to: {target_path}")
        return target_path

    except Exception as e:
        logger.warning(f"OpenAI TTS synthesis error ({e}); falling back to gTTS...")
        return synthesize_with_gtts(text, output_file=output_file)


def synthesize_with_gtts(
    text: str,
    output_file: Optional[Union[str, Path]] = None,
    lang: Optional[str] = None,
    tld: Optional[str] = None,
) -> Optional[Path]:
    """Synthesize text to speech using Google's gTTS service.

    Args:
        text: Text to speak.
        output_file: Target file path. If None, generated automatically in temp_dir.
        lang: Language code (e.g. 'pt', 'en', 'es').
        tld: Top-level domain for accent (e.g. 'com.br', 'com').

    Returns:
        Optional[Path]: Path to generated MP3 file, or None if synthesis failed.
    """
    try:
        from gtts import gTTS
    except ImportError:
        logger.error("gTTS is not installed. Install with: pip install gTTS")
        return None

    lang_code = lang or config.gtts_language
    tld_domain = tld or config.gtts_tld

    if output_file is None:
        target_path = config.temp_dir / f"tts_gtts_{int(time.time() * 1000)}.mp3"
    else:
        target_path = Path(output_file)

    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.debug(f"Synthesizing {len(text)} chars with gTTS (lang={lang_code}, tld={tld_domain})...")
        tts = gTTS(text=text, lang=lang_code, tld=tld_domain)
        tts.save(str(target_path))
        logger.debug(f"gTTS saved to: {target_path}")
        return target_path
    except Exception as e:
        logger.error(f"Google TTS synthesis error: {e}")
        return None


def synthesize_to_bytes(
    text: str,
    engine: Optional[str] = None,
) -> Optional[io.BytesIO]:
    """Synthesize speech directly into an in-memory BytesIO buffer without touching disk.

    Args:
        text: Text to synthesize.
        engine: 'openai' or 'gtts'. Defaults to config.tts_engine.

    Returns:
        Optional[io.BytesIO]: Audio buffer or None on failure.
    """
    selected_engine = (engine or config.tts_engine).lower()

    if selected_engine == "gtts":
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang=config.gtts_language, tld=config.gtts_tld)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            return buffer
        except Exception as e:
            logger.error(f"gTTS in-memory synthesis error: {e}")
            return None

    # OpenAI TTS
    if config.has_openai_key:
        try:
            client = get_openai_client()
            model_name = config.openai_tts_model
            voice_name = config.openai_tts_voice

            if config.openai_base_url and "openrouter.ai" in config.openai_base_url.lower():
                if model_name in ("openai/tts-1", "tts-1", "tts-1-hd"):
                    model_name = "hexgrad/kokoro-82m"
                    if voice_name in ("nova", "alloy", "echo", "fable", "onyx", "shimmer"):
                        voice_name = "af_bella"

            response = client.audio.speech.create(
                model=model_name,
                voice=voice_name,
                input=text,
            )
            buffer = io.BytesIO(response.content)
            buffer.seek(0)
            return buffer
        except Exception as e:
            logger.warning(f"OpenAI in-memory synthesis error ({e}); falling back to gTTS in-memory...")
            return synthesize_to_bytes(text, engine="gtts")
    else:
        # Fallback to gTTS if OpenAI key is not set
        logger.info("OPENAI_API_KEY not configured, falling back to gTTS in-memory...")
        return synthesize_to_bytes(text, engine="gtts")


def synthesize_text(
    text: str,
    output_file: Optional[Union[str, Path]] = None,
    engine: Optional[str] = None,
) -> Optional[Path]:
    """High-level unified TTS synthesis function with automatic engine selection and fallbacks."""
    selected_engine = (engine or config.tts_engine).lower()

    if selected_engine == "openai" and config.has_openai_key:
        path = synthesize_with_openai(text, output_file=output_file)
        if path:
            return path
        logger.warning("OpenAI TTS failed; falling back to gTTS...")

    # Fallback or primary gTTS
    return synthesize_with_gtts(text, output_file=output_file)