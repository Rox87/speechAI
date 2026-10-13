"""SpeechAI: Main entrypoint and comprehensive Command Line Interface (CLI).

Provides interactive voice assistant mode and dedicated subcommands for
Text-to-Speech (TTS), Speech-to-Text (STT), audio playback, and system diagnostics.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure project root is in sys.path when executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import config
from src.core.logger import logger
from src.core.voice_assistant import VoiceAssistant, assistant, listen_and_respond, chat_and_speak
from src.core.audio.recorder import (
    record_audio_to_bytes,
    record_audio_to_file,
    audio_stream_generator,
    check_audio_input_device,
)
from src.core.audio.audio_transcriber import transcribe_audio
from src.core.audio.player import play_audio
from src.core.tts.synthesizer import (
    synthesize_text,
    synthesize_with_openai,
    synthesize_with_gtts,
)
from src.core.utils.temp_file_cleaner import clean_temp_dir


def run_diagnostics() -> bool:
    """Perform self-diagnostic check on the environment and dependencies."""
    logger.info("=" * 60)
    logger.info("Running SpeechAI System Diagnostics...")
    logger.info("=" * 60)
    all_ok = True

    # 1. Python version
    logger.info(f"Python Version: {sys.version.split()[0]} ({sys.platform})")

    # 2. OpenAI API Key & Base URL
    if config.has_openai_key:
        masked_key = config.openai_api_key[:6] + "..." + config.openai_api_key[-4:]
        logger.info(f"[OK] OpenAI API Key configured: {masked_key}")
    elif config.openai_base_url:
        logger.info(f"[INFO] Using custom Base URL without key: {config.openai_base_url}")
    else:
        logger.warning("[WARNING] OpenAI API Key is missing or invalid in .env")
        all_ok = False

    if config.openai_base_url:
        logger.info(f"[OK] Custom Base URL configured: {config.openai_base_url}")

    # 3. Audio Recording (sounddevice)
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devs = [d for d in devices if d.get("max_input_channels", 0) > 0]
        if input_devs:
            default_in = sd.query_devices(kind="input")
            logger.info(f"[OK] Microphone detected: {default_in['name']}")
        else:
            logger.warning("[WARNING] sounddevice loaded, but no input microphone found.")
    except Exception as e:
        logger.warning(f"[WARNING] sounddevice error: {e}")

    # 4. Audio Playback (Pygame / winsound)
    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.quit()
        logger.info("[OK] Pygame audio playback engine initialized successfully.")
    except Exception as e:
        logger.warning(f"[WARNING] Pygame mixer unavailable: {e}")

    # 5. Google TTS (gTTS)
    try:
        import gtts
        logger.info(f"[OK] gTTS installed (v{gtts.__version__})")
    except Exception as e:
        logger.warning(f"[WARNING] gTTS unavailable: {e}")

    # 6. Temp directory
    if config.temp_dir.exists() and config.temp_dir.is_dir():
        logger.info(f"[OK] Temp directory ready: {config.temp_dir}")
    else:
        logger.error(f"[ERROR] Temp directory issue: {config.temp_dir}")
        all_ok = False

    logger.info("=" * 60)
    if all_ok:
        logger.info("All essential components are configured and ready!")
    else:
        logger.warning("Some features may be limited due to missing keys or devices.")
    logger.info("=" * 60)
    return all_ok


def build_parser() -> argparse.ArgumentParser:
    """Build command line argument parser."""
    parser = argparse.ArgumentParser(
        prog="speechai",
        description="SpeechAI: Modular Voice Assistant and Speech Processing Framework.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: assistant
    assistant_parser = subparsers.add_parser("assistant", help="Run the interactive voice assistant")
    assistant_parser.add_argument("--model", type=str, help="OpenAI chat model (e.g. gpt-4o, gpt-4o-mini)")
    assistant_parser.add_argument("--tts", type=str, choices=["openai", "gtts"], help="TTS engine")
    assistant_parser.add_argument("--stt", type=str, choices=["openai", "local"], help="STT engine")
    assistant_parser.add_argument("--base-url", type=str, default=config.openai_base_url, help="Custom API Base URL (e.g. http://localhost:11434/v1)")

    # Command: speak / tts
    speak_parser = subparsers.add_parser("speak", help="Convert text to speech and play or save it")
    speak_parser.add_argument("text", type=str, help="Text to speak")
    speak_parser.add_argument("--engine", type=str, choices=["openai", "gtts"], default=config.tts_engine, help="TTS engine")
    speak_parser.add_argument("--voice", type=str, default=config.openai_tts_voice, help="OpenAI voice (nova, alloy, etc.)")
    speak_parser.add_argument("--save", type=str, help="Save audio to file instead of only playing")
    speak_parser.add_argument("--no-play", action="store_true", help="Do not play audio after synthesis")

    # Command: transcribe / stt
    transcribe_parser = subparsers.add_parser("transcribe", help="Transcribe speech from microphone or file")
    transcribe_parser.add_argument("file", nargs="?", type=str, help="Audio file path (WAV/MP3)")
    transcribe_parser.add_argument("--record", type=float, metavar="SECONDS", help="Record from microphone for N seconds and transcribe")
    transcribe_parser.add_argument("--engine", type=str, choices=["openai", "local"], default=config.stt_engine, help="STT engine")

    # Command: play
    play_parser = subparsers.add_parser("play", help="Play an audio file")
    play_parser.add_argument("file", type=str, help="Path to audio file to play")

    # Command: check
    subparsers.add_parser("check", help="Run environment and hardware diagnostics")

    # Command: clean
    subparsers.add_parser("clean", help="Clean all temporary audio files in temp directory")

    # Command: ui
    ui_parser = subparsers.add_parser("ui", help="Launch interactive Web UI studio")
    ui_parser.add_argument("--port", type=int, default=7860, help="Port to bind (default: 7860)")
    ui_parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address (default: 127.0.0.1)")
    ui_parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")

    return parser


def cli_entrypoint() -> None:
    """CLI handler routing commands to appropriate services."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "assistant" or args.command is None:
        # Default to interactive assistant
        chat_model = getattr(args, "model", None)
        tts = getattr(args, "tts", None)
        stt = getattr(args, "stt", None)
        base_url = getattr(args, "base_url", None)
        va = VoiceAssistant(chat_model=chat_model, tts_engine=tts, stt_engine=stt, base_url=base_url)
        va.run_assistant_loop()

    elif args.command == "ui":
        from src.ui.server import start_server
        port = getattr(args, "port", 7860)
        host = getattr(args, "host", "127.0.0.1")
        open_browser = not getattr(args, "no_browser", False)
        srv = start_server(host=host, port=port, open_browser=open_browser)
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            logger.info("\nEncerrando servidor Web UI...")
            srv.server_close()

    elif args.command == "speak":
        output_file = args.save
        audio_path = synthesize_text(args.text, output_file=output_file, engine=args.engine)
        if audio_path:
            logger.info(f"Synthesized successfully: {audio_path}")
            if not args.no_play:
                play_audio(audio_path)
        else:
            logger.error("Synthesis failed.")
            sys.exit(1)

    elif args.command == "transcribe":
        if args.record:
            buffer = record_audio_to_bytes(duration=args.record)
            transcript = transcribe_audio(buffer, engine=args.engine)
            logger.info(f"Transcription: {transcript}")
        elif args.file:
            transcript = transcribe_audio(args.file, engine=args.engine)
            logger.info(f"Transcription: {transcript}")
        else:
            logger.error("Please specify an audio file or use --record <seconds>.")
            sys.exit(1)

    elif args.command == "play":
        if not play_audio(args.file):
            sys.exit(1)

    elif args.command == "check":
        run_diagnostics()

    elif args.command == "clean":
        count = clean_temp_dir()
        logger.info(f"Cleaned {count} temporary files.")


# Backwards compatible exports
__all__ = [
    "audio_stream_generator",
    "record_audio_to_bytes",
    "listen_and_respond",
    "chat_and_speak",
    "cli_entrypoint",
    "run_diagnostics",
]

if __name__ == "__main__":
    cli_entrypoint()
