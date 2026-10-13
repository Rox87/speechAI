"""Unit tests for configuration module."""

import unittest
from pathlib import Path
from src.core.config import AppConfig, config


class TestAppConfig(unittest.TestCase):
    """Test AppConfig default initialization and properties."""

    def test_default_config_exists(self):
        self.assertIsNotNone(config)
        self.assertIsInstance(config.root_dir, Path)
        self.assertIsInstance(config.temp_dir, Path)
        self.assertTrue(config.temp_dir.exists())

    def test_custom_config(self):
        custom = AppConfig(
            chat_model="gpt-4o",
            openai_tts_voice="alloy",
            stt_engine="openai",
            tts_engine="gtts",
        )
        self.assertEqual(custom.chat_model, "gpt-4o")
        self.assertEqual(custom.openai_tts_voice, "alloy")
        self.assertEqual(custom.tts_engine, "gtts")

    def test_has_openai_key_false_by_default_or_placeholder(self):
        cfg = AppConfig(openai_api_key="")
        self.assertFalse(cfg.has_openai_key)

        cfg_placeholder = AppConfig(openai_api_key="your_openai_api_key_here")
        self.assertFalse(cfg_placeholder.has_openai_key)

        cfg_real = AppConfig(openai_api_key="sk-proj-1234567890abcdef")
        self.assertTrue(cfg_real.has_openai_key)

    def test_base_url_configuration(self):
        cfg = AppConfig(openai_base_url="  https://api.groq.com/openai/v1  ")
        self.assertEqual(cfg.openai_base_url, "https://api.groq.com/openai/v1")

        cfg_empty = AppConfig(openai_base_url="   ")
        self.assertIsNone(cfg_empty.openai_base_url)

    def test_is_openai_configured(self):
        # Neither key nor base_url
        cfg_none = AppConfig(openai_api_key="", openai_base_url=None)
        self.assertFalse(cfg_none.is_openai_configured)

        # Key only
        cfg_key = AppConfig(openai_api_key="sk-real-key", openai_base_url=None)
        self.assertTrue(cfg_key.is_openai_configured)

        # Base URL only (e.g. Ollama local instance)
        cfg_url = AppConfig(openai_api_key="", openai_base_url="http://localhost:11434/v1")
        self.assertTrue(cfg_url.is_openai_configured)

    def test_base_url_env_resolution(self):
        import os
        from unittest.mock import patch
        from src.core.config import _resolve_base_url

        with patch.dict(os.environ, {"OPENAI_BASE_URL": "http://custom-url:8000/v1"}, clear=False):
            self.assertEqual(_resolve_base_url(), "http://custom-url:8000/v1")

        with patch.dict(os.environ, {"OPENAI_BASE_URL": "", "BASE_URL": "http://fallback-url:11434/v1"}, clear=False):
            self.assertEqual(_resolve_base_url(), "http://fallback-url:11434/v1")

        with patch.dict(os.environ, {"OPENAI_BASE_URL": "", "BASE_URL": "", "OPENAI_API_BASE": "http://legacy-url:8080/v1"}, clear=False):
            self.assertEqual(_resolve_base_url(), "http://legacy-url:8080/v1")


if __name__ == "__main__":
    unittest.main()
