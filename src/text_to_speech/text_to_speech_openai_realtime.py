"""Real-time OpenAI TTS playback script and functions."""

from src.realtime_processing.realtime_openai import speak, time_elapsed

__all__ = ["speak", "time_elapsed"]

if __name__ == "__main__":
    import sys
    sample_text = sys.argv[1] if len(sys.argv) > 1 else "Hello from OpenAI Realtime TTS!"
    speak(sample_text)
