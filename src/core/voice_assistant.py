"""Core Voice Assistant orchestrator.

Integrates microphone capture, speech-to-text (STT), OpenAI LLM conversational reasoning,
and text-to-speech (TTS) playback in a continuous interactive dialogue loop.
"""

from __future__ import annotations

import sys
from typing import Optional, List, Dict, Tuple

from src.core.logger import logger
from src.core.config import config
from src.core.client import get_openai_client
from src.core.audio.recorder import record_audio_to_bytes, check_audio_input_device
from src.core.audio.audio_transcriber import transcribe_audio
from src.core.audio.player import player
from src.core.tts.synthesizer import synthesize_to_bytes, synthesize_text
from src.core.utils.temp_file_cleaner import clean_temp_dir


EXIT_COMMANDS = {
    "exit", "quit", "bye", "goodbye", "stop",
    "sair", "tchau", "encerrar", "parar", "desligar"
}


class VoiceAssistant:
    """Conversational voice assistant managing STT, reasoning, and TTS."""

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        chat_model: Optional[str] = None,
        tts_engine: Optional[str] = None,
        stt_engine: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.chat_model = chat_model or config.chat_model
        self.tts_engine = (tts_engine or config.tts_engine).lower()
        self.stt_engine = (stt_engine or config.stt_engine).lower()
        self.base_url = base_url or config.openai_base_url
        self.system_prompt = system_prompt or (
            "Você é um assistente de voz prestativo, inteligente e conciso. "
            "Responda sempre em português do Brasil de forma breve e natural para conversa falada."
        )
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def reset_history(self) -> None:
        """Reset conversation memory to initial system prompt."""
        self.history = [{"role": "system", "content": self.system_prompt}]
        logger.info("Conversation history cleared.")

    def is_exit_command(self, text: str) -> bool:
        """Check if transcribed user text represents an exit/termination command."""
        normalized = text.strip().lower().rstrip(".,!?")
        if not normalized:
            return False
        # Exact match or short phrase starting with exit command
        words = normalized.split()
        return normalized in EXIT_COMMANDS or (len(words) <= 2 and words[0] in EXIT_COMMANDS)

    def chat_and_speak(self, prompt: str, speak: bool = True) -> str:
        """Query LLM with conversational context and speak the generated answer.

        Args:
            prompt: User utterance or prompt string.
            speak: Whether to play the audio locally via player (default: True).

        Returns:
            str: Assistant response text.
        """
        if not prompt or not prompt.strip():
            return ""

        if not config.has_openai_key:
            msg = "Chave da OpenAI não configurada no arquivo .env."
            logger.error(msg)
            if speak:
                self._speak(msg)
            return msg

        try:
            client = get_openai_client(base_url=self.base_url)
            self.history.append({"role": "user", "content": prompt})

            logger.info(f"Querying OpenAI ({self.chat_model})...")
            response = client.chat.completions.create(
                model=self.chat_model,
                messages=self.history,
                temperature=0.7,
            )

            assistant_text = response.choices[0].message.content or ""
            self.history.append({"role": "assistant", "content": assistant_text})
            logger.info(f"Assistant: {assistant_text}")

            if speak:
                self._speak(assistant_text)
            return assistant_text

        except Exception as e:
            logger.error(f"Error in chat_and_speak: {e}")
            err_msg = f"Desculpe, ocorreu um erro: {e}"
            if speak:
                self._speak(err_msg)
            return err_msg

    def _speak(self, text: str) -> bool:
        """Internal helper to synthesize and play text."""
        audio_buffer = synthesize_to_bytes(text, engine=self.tts_engine)
        if audio_buffer:
            return player.play(audio_buffer, block=True)

        # Fallback to file-based synthesis
        temp_file = config.temp_dir / "assistant_response.mp3"
        result_file = synthesize_text(text, output_file=temp_file, engine=self.tts_engine)
        if result_file:
            return player.play(result_file, block=True)
        return False

    def listen_and_respond_once(self, speak: bool = True) -> Tuple[str, str, bool]:
        """Perform one complete voice turn: record, transcribe, reply.

        Args:
            speak: Whether to play the audio response locally via player (default: True).

        Returns:
            Tuple[str, str, bool]: (user_text, assistant_text, should_continue)
        """
        try:
            # 1. Record audio
            audio_buffer = record_audio_to_bytes()

            # 2. Transcribe audio to text
            user_text = transcribe_audio(audio_buffer, engine=self.stt_engine)
            if not user_text or not user_text.strip():
                logger.info("No speech detected.")
                return "", "", True

            logger.info(f"You said: {user_text}")

            # 3. Check for exit
            if self.is_exit_command(user_text):
                farewell = "Goodbye! Até logo!"
                logger.info(farewell)
                if speak:
                    self._speak(farewell)
                return user_text, farewell, False

            # 4. Generate response and speak
            assistant_reply = self.chat_and_speak(user_text, speak=speak)
            return user_text, assistant_reply, True

        except ValueError as e:
            if "OPENAI_API_KEY" in str(e):
                logger.error(f"Configuração necessária: {e}")
                return "", str(e), False
            logger.error(f"Erro de valor: {e}")
            return "", str(e), True
        except Exception as e:
            logger.error(f"Error during voice interaction turn: {e}")
            return "", str(e), True

    def run_assistant_loop(self) -> None:
        """Run continuous voice assistant loop until user exits or interrupts."""
        # Check if OpenAI key is configured
        if not config.has_openai_key and self.stt_engine == "openai":
            logger.warning("=" * 60)
            logger.warning("[AVISO] Chave OPENAI_API_KEY não configurada no arquivo .env!")
            logger.warning("O assistente interativo requer a chave da OpenAI para STT e ChatGPT.")
            logger.warning("Crie ou edite seu arquivo .env com base no .env.example:")
            logger.info("    cp .env.example .env")
            logger.info("\nVocê pode testar outras funcionalidades sem chave agora mesmo:")
            logger.info("  1. Diagnóstico do sistema:      python src/main.py check")
            logger.info("  2. Síntese de voz com gTTS:     python src/main.py speak \"Olá!\" --engine gtts")
            logger.info("  3. Ver todas as opções:         python src/main.py --help")
            logger.warning("=" * 60)
            return

        logger.info("=" * 60)
        logger.info("SpeechAI Voice Assistant is active!")
        logger.info(f"Chat Model: {self.chat_model} | TTS: {self.tts_engine} | STT: {self.stt_engine}")
        logger.info("Speak into your microphone. Say 'sair' or 'exit' to quit.")
        logger.info("=" * 60)

        # Clean any leftover temp files on startup
        clean_temp_dir()

        while True:
            try:
                _, _, should_continue = self.listen_and_respond_once()
                if not should_continue:
                    break
            except KeyboardInterrupt:
                logger.info("\nUser interrupted. Exiting voice assistant...")
                break
            except Exception as e:
                logger.error(f"Loop error: {e}")

        # Clean temporary files on exit
        clean_temp_dir()
        logger.info("Voice assistant stopped.")


# Default instance
assistant = VoiceAssistant()


# Backwards compatible functions
def chat_and_speak(prompt: str) -> str:
    """Backwards compatible chat_and_speak function."""
    return assistant.chat_and_speak(prompt)


def listen_and_respond() -> None:
    """Backwards compatible voice assistant loop."""
    assistant.run_assistant_loop()


if __name__ == "__main__":
    listen_and_respond()
