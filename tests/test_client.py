"""Unit tests for OpenAI client provider and base_url handling."""

import unittest
from unittest.mock import patch, MagicMock

from src.core.config import AppConfig
from src.core.client import get_openai_client, reset_client


class TestOpenAIClient(unittest.TestCase):
    """Test get_openai_client instantiation, caching, and base_url passing."""

    def setUp(self):
        reset_client()

    def tearDown(self):
        reset_client()

    def test_missing_key_and_no_base_url_raises_error(self):
        with patch("src.core.config.config.openai_api_key", ""):
            with patch("src.core.config.config.openai_base_url", None):
                with self.assertRaises(ValueError):
                    get_openai_client(force_new=True)

    @patch("src.core.client.OpenAI")
    def test_client_creation_with_key_default_base_url(self, mock_openai):
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance

        with patch("src.core.config.config.openai_api_key", "sk-validkey1234567890"):
            with patch("src.core.config.config.openai_base_url", None):
                client = get_openai_client(force_new=True)
                mock_openai.assert_called_once_with(api_key="sk-validkey1234567890")
                self.assertEqual(client, mock_instance)

    @patch("src.core.client.OpenAI")
    def test_client_creation_with_custom_base_url_from_config(self, mock_openai):
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance

        with patch("src.core.config.config.openai_api_key", "sk-validkey1234567890"):
            with patch("src.core.config.config.openai_base_url", "http://localhost:11434/v1"):
                client = get_openai_client(force_new=True)
                mock_openai.assert_called_once_with(
                    api_key="sk-validkey1234567890",
                    base_url="http://localhost:11434/v1",
                )
                self.assertEqual(client, mock_instance)

    def test_missing_key_with_base_url_raises_error(self):
        with patch("src.core.config.config.openai_api_key", ""):
            with patch("src.core.config.config.openai_base_url", "http://localhost:11434/v1"):
                with self.assertRaises(ValueError):
                    get_openai_client(force_new=True)

    @patch("src.core.client.OpenAI")
    def test_client_caching_and_force_new(self, mock_openai):
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance

        with patch("src.core.config.config.openai_api_key", "sk-validkey1234567890"):
            with patch("src.core.config.config.openai_base_url", "http://localhost:11434/v1"):
                c1 = get_openai_client()
                c2 = get_openai_client()
                self.assertIs(c1, c2)
                self.assertEqual(mock_openai.call_count, 1)

                c3 = get_openai_client(force_new=True)
                self.assertEqual(mock_openai.call_count, 2)


if __name__ == "__main__":
    unittest.main()
