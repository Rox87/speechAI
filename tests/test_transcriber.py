"""Unit tests for audio transcription module."""

import io
import unittest
from unittest.mock import patch, MagicMock

from src.core.audio.audio_transcriber import (
    transcribe_with_openai,
    transcribe_audio,
)


class TestAudioTranscriber(unittest.TestCase):
    """Test STT transcription with OpenAI Whisper and local fallback."""

    def test_transcribe_with_openai_missing_key(self):
        with patch("src.core.config.config.openai_api_key", ""):
            with self.assertRaises(ValueError):
                transcribe_with_openai(io.BytesIO(b"dummy"))

    @patch("src.core.audio.audio_transcriber.get_openai_client")
    def test_transcribe_with_openai_bytesio(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_transcription = MagicMock()
        mock_transcription.text = "Hello from audio transcription"
        mock_client.audio.transcriptions.create.return_value = mock_transcription

        with patch("src.core.config.config.openai_api_key", "sk-validkey1234567890"):
            buffer = io.BytesIO(b"RIFFWAVE...")
            result = transcribe_with_openai(buffer)
            self.assertEqual(result, "Hello from audio transcription")

    @patch("src.core.audio.audio_transcriber.transcribe_with_openai")
    def test_transcribe_audio_dispatches_to_openai(self, mock_transcribe_openai):
        mock_transcribe_openai.return_value = "Test response"
        buffer = io.BytesIO(b"RIFFWAVE...")
        res = transcribe_audio(buffer, engine="openai")
        self.assertEqual(res, "Test response")


if __name__ == "__main__":
    unittest.main()
