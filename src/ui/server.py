"""SpeechAI Web UI Server.

Provides a lightweight, zero-dependency modern HTTP server serving a single-page
application with REST APIs for live voice assistant, speech synthesis, transcription,
and environment diagnostics.
"""

from __future__ import annotations

import base64
import io
import json
import mimetypes
import os
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.config import config, ROOT_DIR
from src.core.logger import logger
from src.core.tts.synthesizer import synthesize_to_bytes
from src.core.audio.audio_transcriber import transcribe_audio
from src.core.voice_assistant import assistant
from src.core.tts.chatgpt_tts_handler import default_handler

STATIC_DIR = Path(__file__).resolve().parent / "static"


class SpeechAIRequestHandler(SimpleHTTPRequestHandler):
    """Custom request handler dispatching REST APIs and serving UI assets."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def _set_headers(self, status: int = 200, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self._set_headers(status=204)

    def _read_json(self) -> Dict[str, Any]:
        """Read and parse JSON body from incoming POST request."""
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_GET(self) -> None:
        """Handle GET requests for static files and query endpoints."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/config":
            self.handle_get_config()
        elif path == "/api/diagnostics":
            self.handle_get_diagnostics()
        elif path == "/api/synthesize":
            self.handle_get_synthesize(parsed.query)
        elif path in ("/", "/index.html", "/style.css", "/app.js"):
            file_name = "index.html" if path == "/" else path.lstrip("/")
            file_path = STATIC_DIR / file_name
            if file_path.exists():
                mime, _ = mimetypes.guess_type(str(file_path))
                self._set_headers(200, mime or "text/plain")
                self.wfile.write(file_path.read_bytes())
            else:
                self._set_headers(404, "text/plain")
                self.wfile.write(b"404 Not Found")
        else:
            super().do_GET()

    def do_POST(self) -> None:
        """Handle POST requests for AI actions."""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/chat":
            self.handle_post_chat()
        elif path == "/api/synthesize":
            self.handle_post_synthesize()
        elif path == "/api/transcribe":
            self.handle_post_transcribe()
        elif path == "/api/voice-turn":
            self.handle_post_voice_turn()
        elif path == "/api/config":
            self.handle_post_config()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    # ------------------- Handler Endpoints ------------------- #

    def handle_get_config(self) -> None:
        """Return active environment configuration."""
        masked_key = ""
        if config.has_openai_key:
            masked_key = config.openai_api_key[:6] + "..." + config.openai_api_key[-4:]

        data = {
            "openai_api_key_masked": masked_key,
            "has_key": config.has_openai_key,
            "openai_base_url": config.openai_base_url or "",
            "chat_model": config.chat_model,
            "openai_whisper_model": config.openai_whisper_model,
            "stt_engine": config.stt_engine,
            "tts_engine": config.tts_engine,
            "openai_tts_model": config.openai_tts_model,
            "openai_tts_voice": config.openai_tts_voice,
            "gtts_language": config.gtts_language,
            "gtts_tld": config.gtts_tld,
            "playback_engine": config.playback_engine,
            "sample_rate": config.sample_rate,
            "record_duration": config.record_duration,
        }
        self._set_headers(200)
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def handle_get_diagnostics(self) -> None:
        """Perform system checks and return structured diagnostic status."""
        checks = []

        # 1. Key & Provider
        if config.has_openai_key:
            checks.append({
                "name": "API Key",
                "status": "ok",
                "message": f"Configurada ({config.openai_api_key[:6]}...)"
            })
        else:
            checks.append({
                "name": "API Key",
                "status": "warning",
                "message": "Não configurada no .env"
            })

        # 2. Base URL
        if config.openai_base_url:
            checks.append({
                "name": "Base URL",
                "status": "ok",
                "message": config.openai_base_url
            })
        else:
            checks.append({
                "name": "Base URL",
                "status": "info",
                "message": "Padrão oficial OpenAI (https://api.openai.com/v1)"
            })

        # 3. Microfone (Sounddevice)
        try:
            import sounddevice as sd
            devs = sd.query_devices()
            in_devs = [d for d in devs if d.get("max_input_channels", 0) > 0]
            if in_devs:
                checks.append({
                    "name": "Microfone",
                    "status": "ok",
                    "message": f"{len(in_devs)} dispositivo(s) detectado(s)"
                })
            else:
                checks.append({
                    "name": "Microfone",
                    "status": "warning",
                    "message": "Nenhum microfone de entrada encontrado"
                })
        except Exception as e:
            checks.append({"name": "Microfone", "status": "error", "message": str(e)})

        # 4. Audio Playback (Pygame)
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.quit()
            checks.append({"name": "Player Pygame", "status": "ok", "message": "Disponível e operacional"})
        except Exception as e:
            checks.append({"name": "Player Pygame", "status": "warning", "message": str(e)})

        # 5. gTTS
        try:
            import gtts
            checks.append({"name": "Google TTS (gTTS)", "status": "ok", "message": f"Instalado (v{gtts.__version__})"})
        except Exception as e:
            checks.append({"name": "Google TTS (gTTS)", "status": "warning", "message": str(e)})

        self._set_headers(200)
        self.wfile.write(json.dumps({"checks": checks}).encode("utf-8"))

    def handle_get_synthesize(self, query_str: str) -> None:
        """Stream synthesized audio via GET query params (ideal for HTML5 audio tags)."""
        qs = urllib.parse.parse_qs(query_str)
        text = qs.get("text", [""])[0]
        engine = qs.get("engine", [config.tts_engine])[0]

        if not text:
            self._set_headers(400, "text/plain")
            self.wfile.write(b"Parametro 'text' e obrigatorio")
            return

        buffer = synthesize_to_bytes(text, engine=engine)
        if buffer:
            self._set_headers(200, "audio/mpeg")
            self.wfile.write(buffer.getvalue())
        else:
            self._set_headers(500, "text/plain")
            self.wfile.write(b"Falha na sintese de audio")

    def handle_post_chat(self) -> None:
        """Receive prompt and get LLM response from OpenRouter/OpenAI."""
        body = self._read_json()
        prompt = body.get("message", "").strip()
        system_prompt = body.get("system_prompt")

        if not prompt:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Mensagem vazia"}).encode("utf-8"))
            return

        if system_prompt:
            default_handler.reset_conversation(system_prompt)

        reply = default_handler.get_chatgpt_response(prompt)
        self._set_headers(200)
        self.wfile.write(json.dumps({"reply": reply}).encode("utf-8"))

    def handle_post_synthesize(self) -> None:
        """Synthesize text and return base64 audio and metadata."""
        body = self._read_json()
        text = body.get("text", "").strip()
        engine = body.get("engine", config.tts_engine)

        if not text:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Texto vazio"}).encode("utf-8"))
            return

        buffer = synthesize_to_bytes(text, engine=engine)
        if buffer:
            audio_b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "audio_base64": f"data:audio/mp3;base64,{audio_b64}",
                "text": text,
                "engine": engine
            }).encode("utf-8"))
        else:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": "Falha na síntese de áudio"}).encode("utf-8"))

    def handle_post_transcribe(self) -> None:
        """Transcribe base64 audio or raw audio data."""
        body = self._read_json()
        audio_b64 = body.get("audio_base64", "")
        engine = body.get("engine", config.stt_engine)

        if not audio_b64:
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": "Nenhum áudio enviado"}).encode("utf-8"))
            return

        # Strip data URL prefix if present
        if "," in audio_b64:
            audio_b64 = audio_b64.split(",", 1)[1]

        try:
            audio_bytes = base64.b64decode(audio_b64)
            audio_buffer = io.BytesIO(audio_bytes)
            transcript = transcribe_audio(audio_buffer, engine=engine)
            self._set_headers(200)
            self.wfile.write(json.dumps({"transcript": transcript}).encode("utf-8"))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_post_voice_turn(self) -> None:
        """Execute one complete live turn from local hardware microphone."""
        try:
            user_text, assistant_text, should_continue = assistant.listen_and_respond_once()
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "user_text": user_text,
                "assistant_text": assistant_text,
                "should_continue": should_continue
            }).encode("utf-8"))
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

    def handle_post_config(self) -> None:
        """Update settings and persist to .env file."""
        body = self._read_json()
        env_path = ROOT_DIR / ".env"

        # Read existing .env lines
        existing_lines = []
        if env_path.exists():
            existing_lines = env_path.read_text(encoding="utf-8").splitlines()

        def update_or_append(key: str, val: str) -> None:
            nonlocal existing_lines
            found = False
            for i, line in enumerate(existing_lines):
                if line.strip().startswith(f"{key}=") or line.strip().startswith(f"#{key}="):
                    existing_lines[i] = f"{key}={val}"
                    found = True
                    break
            if not found:
                existing_lines.append(f"{key}={val}")

        for k, v in body.items():
            k_upper = k.upper()
            if hasattr(config, k.lower()):
                setattr(config, k.lower(), v)
            update_or_append(k_upper, str(v))

        env_path.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")
        self._set_headers(200)
        self.wfile.write(json.dumps({"status": "saved"}).encode("utf-8"))


def start_server(host: str = "127.0.0.1", port: int = 7860, open_browser: bool = True) -> ThreadingHTTPServer:
    """Launch the Web UI HTTP server and optionally open the web browser."""
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer((host, port), SpeechAIRequestHandler)
    url = f"http://{host}:{port}"
    logger.info("=" * 60)
    logger.info(f"🎙️ SpeechAI Web UI iniciado em: {url}")
    logger.info("Pressione Ctrl+C no terminal para encerrar o servidor.")
    logger.info("=" * 60)

    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()

    return server


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7860
    srv = start_server(port=port, open_browser=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        logger.info("\nEncerrando servidor Web UI...")
        srv.server_close()
