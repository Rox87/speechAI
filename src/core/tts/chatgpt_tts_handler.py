"""ChatGPT conversational Text-to-Speech handler with streaming and playback capabilities."""

from __future__ import annotations

import io
from pathlib import Path
from typing import List, Dict, Optional, Union

from openai import OpenAI
from src.core.logger import logger
from src.core.config import config
from src.core.client import get_openai_client
from src.core.audio.player import player, play_audio
from src.core.tts.synthesizer import synthesize_to_bytes, synthesize_text


class ChatGPTTTSHandler:
    """Manages conversational dialogue with OpenAI Chat and synthesizes responses to audio."""

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        tts_engine: Optional[str] = None,
        base_url: Optional[str] = None,
    ):
        self.model = model or config.chat_model
        self.tts_engine = (tts_engine or config.tts_engine).lower()
        self.base_url = base_url or config.openai_base_url
        self.system_prompt = system_prompt or (
            "Você é um assistente de voz prestativo, inteligente, caloroso e conciso. "
            "Responda sempre em português do Brasil com fala fluida, natural e amigável. "
            "Nunca use formatação markdown, marcadores de tópicos (bullet points), asteriscos ou tabelas, "
            "pois sua resposta será sintetizada em voz alta. "
            "Use pontuação expressiva com vírgulas e pausas naturais de conversação."
        )
        self.history: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]

    def reset_conversation(self, new_system_prompt: Optional[str] = None) -> None:
        """Reset conversational context memory."""
        if new_system_prompt:
            self.system_prompt = new_system_prompt
        self.history = [{"role": "system", "content": self.system_prompt}]
        logger.info("Conversation history reset.")

    def get_chatgpt_response(self, prompt: str) -> str:
        """Send prompt to OpenAI Chat API and track dialog context.

        Args:
            prompt: User speech transcript or prompt.

        Returns:
            str: Assistant response message.
        """
        if not config.has_openai_key:
            return "OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file."

        try:
            client = get_openai_client(base_url=self.base_url)
            self.history.append({"role": "user", "content": prompt})

            logger.info(f"Generating LLM response using {self.model}...")
            response = client.chat.completions.create(
                model=self.model,
                messages=self.history,
                temperature=0.7,
            )
            assistant_message = response.choices[0].message.content or ""
            self.history.append({"role": "assistant", "content": assistant_message})
            return assistant_message

        except Exception as e:
            logger.error(f"Error communicating with OpenAI Chat API: {e}")
            return f"Desculpe, ocorreu um erro ao processar sua resposta: {e}"

    def generate_audio_file(self, text: str) -> Union[Path, io.BytesIO]:
        """Generate audio from text, preferring in-memory BytesIO for speed."""
        audio_buffer = synthesize_to_bytes(text, engine=self.tts_engine)
        if audio_buffer:
            return audio_buffer

        # Fallback to physical temp file
        temp_file = config.temp_dir / f"chat_tts_{int(Path('.').stat().st_mtime)}.mp3"
        result_file = synthesize_text(text, output_file=temp_file, engine=self.tts_engine)
        if not result_file:
            raise RuntimeError("Failed to synthesize audio from text response.")
        return result_file

    def speak(self, text: str) -> bool:
        """Synthesize and immediately play audio for the given text."""
        try:
            audio_source = self.generate_audio_file(text)
            return player.play(audio_source, block=True)
        except Exception as e:
            logger.error(f"Error in TTS playback: {e}")
            return False

    def chat_and_speak(self, prompt: str) -> str:
        """Process conversational prompt and speak the answer.

        Args:
            prompt: User utterance.

        Returns:
            str: Assistant response text.
        """
        response_text = self.get_chatgpt_response(prompt)
        logger.info(f"Assistant: {response_text}")
        self.speak(response_text)
        return response_text


# Global handler instance
default_handler = ChatGPTTTSHandler()


# Backwards compatibility module-level functions
def get_chatgpt_response(prompt: str) -> str:
    """Retrieve response from ChatGPT using default handler."""
    return default_handler.get_chatgpt_response(prompt)


def generate_audio_file(text: str) -> Union[Path, io.BytesIO]:
    """Generate audio file or buffer from text."""
    return default_handler.generate_audio_file(text)


def chat_and_speak(prompt: str) -> str:
    """Process user prompt and speak response."""
    return default_handler.chat_and_speak(prompt)


if __name__ == "__main__":
    chat_and_speak("Hello! How can I help you today?")
