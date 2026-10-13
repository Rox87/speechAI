"""Audio recording module utilizing sounddevice with in-memory WAV encoding."""

from __future__ import annotations

import io
import wave
from pathlib import Path
from typing import Generator, Optional, Union

from src.core.logger import logger
from src.core.config import config


def check_audio_input_device() -> bool:
    """Check if at least one audio input device (microphone) is available."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = [d for d in devices if d.get("max_input_channels", 0) > 0]
        return len(input_devices) > 0
    except Exception as e:
        logger.warning(f"Unable to query audio input devices: {e}")
        return False


def record_audio_to_bytes(
    duration: Optional[float] = None,
    samplerate: Optional[int] = None,
    channels: Optional[int] = None,
) -> io.BytesIO:
    """Record audio from default microphone directly into an in-memory WAV BytesIO buffer.

    Args:
        duration: Recording duration in seconds. Defaults to config.record_duration.
        samplerate: Sample rate in Hz (e.g. 16000 or 44100). Defaults to config.sample_rate.
        channels: Number of audio channels (1=mono, 2=stereo). Defaults to config.channels.

    Returns:
        io.BytesIO: Buffer containing complete WAV audio data ready for Whisper or storage.
    """
    duration = duration or config.record_duration
    samplerate = samplerate or config.sample_rate
    channels = channels or config.channels

    try:
        import sounddevice as sd
    except ImportError:
        raise RuntimeError("sounddevice is not installed. Run: pip install sounddevice")

    logger.info(f"Recording audio for {duration:.1f}s ({samplerate}Hz, {channels}ch)...")
    try:
        total_frames = int(duration * samplerate)
        audio_data = sd.rec(total_frames, samplerate=samplerate, channels=channels, dtype="int16")
        sd.wait()
        logger.info("Recording complete.")
    except Exception as e:
        logger.error(f"Failed to record audio from microphone: {e}")
        raise

    # Package into standard RIFF WAV container in memory
    audio_buffer = io.BytesIO()
    with wave.open(audio_buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit PCM = 2 bytes per sample
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())

    audio_buffer.seek(0)
    return audio_buffer


def record_audio_to_file(
    output_path: Union[str, Path],
    duration: Optional[float] = None,
    samplerate: Optional[int] = None,
    channels: Optional[int] = None,
) -> Path:
    """Record audio from default microphone and save directly to a WAV file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    buffer = record_audio_to_bytes(duration=duration, samplerate=samplerate, channels=channels)
    with open(output_path, "wb") as f:
        f.write(buffer.getvalue())

    logger.info(f"Recorded audio saved to: {output_path}")
    return output_path


def audio_stream_generator(
    chunk_duration: float = 3.0,
    samplerate: Optional[int] = None,
    channels: Optional[int] = None,
) -> Generator[io.BytesIO, None, None]:
    """Continuously record audio chunks and yield WAV BytesIO buffers.

    Args:
        chunk_duration: Length of each slice in seconds.
        samplerate: Audio sample rate.
        channels: Number of channels.

    Yields:
        io.BytesIO: Audio buffer for each chunk.
    """
    samplerate = samplerate or config.sample_rate
    channels = channels or config.channels

    while True:
        try:
            chunk = record_audio_to_bytes(
                duration=chunk_duration,
                samplerate=samplerate,
                channels=channels
            )
            yield chunk
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Error in audio stream chunk: {e}")
            break


if __name__ == "__main__":
    test_file = config.temp_dir / "test_recording.wav"
    record_audio_to_file(test_file, duration=3.0)
