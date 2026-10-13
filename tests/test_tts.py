"""Unit tests for Text-to-Speech synthesis."""

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.tts.synthesizer import (
    synthesize_with_openai,
    synthesize_with_gtts,
    synthesize_to_bytes,
)


class TestTTSSynthesizer(unittest.TestCase):
    """Test TTS synthesis functions and engine dispatch."""

    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        for f in self.temp_dir.glob("*"):
            try:
                f.unlink()
            except Exception:
                pass
        try:
            self.temp_dir.rmdir()
        except Exception:
            pass

    def test_synthesize_with_openai_no_key(self):
        with patch("src.core.config.config.openai_api_key", ""):
            result = synthesize_with_openai("Hello")
            self.assertIsNone(result)

    @patch("src.core.tts.synthesizer.get_openai_client")
    def test_synthesize_with_openai_success(self, mock_get_client):
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = b"fake-mp3-bytes"
        mock_response.write_to_file.side_effect = lambda p: Path(p).write_bytes(b"fake-mp3-bytes")
        mock_client.audio.speech.create.return_value = mock_response

        target_file = self.temp_dir / "test.mp3"
        with patch("src.core.config.config.openai_api_key", "sk-validkey1234567890"):
            out = synthesize_with_openai("Hello world", output_file=target_file)
            self.assertIsNotNone(out)
            self.assertTrue(target_file.exists())
            self.assertEqual(target_file.read_bytes(), b"fake-mp3-bytes")

    @patch("gtts.gTTS")
    def test_synthesize_with_gtts_success(self, mock_gtts_cls):
        mock_tts = MagicMock()
        mock_gtts_cls.return_value = mock_tts

        def fake_save(filename):
            Path(filename).write_bytes(b"gtts-audio")

        mock_tts.save.side_effect = fake_save

        target_file = self.temp_dir / "gtts_test.mp3"
        out = synthesize_with_gtts("Olá mundo", output_file=target_file, lang="pt")
        self.assertIsNotNone(out)
        self.assertTrue(target_file.exists())
        self.assertEqual(target_file.read_bytes(), b"gtts-audio")

    @patch("gtts.gTTS")
    def test_synthesize_to_bytes_gtts(self, mock_gtts_cls):
        mock_tts = MagicMock()
        mock_gtts_cls.return_value = mock_tts

        def fake_write_to_fp(fp):
            fp.write(b"in-memory-gtts-bytes")

        mock_tts.write_to_fp.side_effect = fake_write_to_fp

        buffer = synthesize_to_bytes("Teste em memória", engine="gtts")
        self.assertIsNotNone(buffer)
        self.assertIsInstance(buffer, io.BytesIO)
        self.assertEqual(buffer.getvalue(), b"in-memory-gtts-bytes")


if __name__ == "__main__":
    unittest.main()
