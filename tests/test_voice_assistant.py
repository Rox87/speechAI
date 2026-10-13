"""Unit tests for VoiceAssistant conversation and logic."""

import unittest
from unittest.mock import patch, MagicMock

from src.core.voice_assistant import VoiceAssistant


class TestVoiceAssistant(unittest.TestCase):
    """Test VoiceAssistant conversation management and exit parsing."""

    def setUp(self):
        self.assistant = VoiceAssistant(
            system_prompt="Test system prompt",
            chat_model="gpt-4o-mini",
            tts_engine="gtts",
        )

    def test_initial_state(self):
        self.assertEqual(len(self.assistant.history), 1)
        self.assertEqual(self.assistant.history[0]["role"], "system")
        self.assertEqual(self.assistant.history[0]["content"], "Test system prompt")

    def test_reset_history(self):
        self.assistant.history.append({"role": "user", "content": "Hi"})
        self.assistant.history.append({"role": "assistant", "content": "Hello"})
        self.assertEqual(len(self.assistant.history), 3)

        self.assistant.reset_history()
        self.assertEqual(len(self.assistant.history), 1)
        self.assertEqual(self.assistant.history[0]["role"], "system")

    def test_is_exit_command(self):
        self.assertTrue(self.assistant.is_exit_command("exit"))
        self.assertTrue(self.assistant.is_exit_command("QUIT"))
        self.assertTrue(self.assistant.is_exit_command("bye!"))
        self.assertTrue(self.assistant.is_exit_command("sair."))
        self.assertTrue(self.assistant.is_exit_command("tchau!"))
        self.assertTrue(self.assistant.is_exit_command("encerrar"))

        self.assertFalse(self.assistant.is_exit_command("qual é a previsão do tempo?"))
        self.assertFalse(self.assistant.is_exit_command("say bye to someone"))
        self.assertFalse(self.assistant.is_exit_command(""))

    @patch("src.core.voice_assistant.VoiceAssistant._speak")
    @patch("src.core.voice_assistant.get_openai_client")
    def test_chat_and_speak(self, mock_get_client, mock_speak):
        mock_speak.return_value = True
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "I am doing well, thank you!"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.core.config.config.openai_api_key", "sk-validkey1234567890"):
            reply = self.assistant.chat_and_speak("How are you?")
            self.assertEqual(reply, "I am doing well, thank you!")
            self.assertEqual(len(self.assistant.history), 3)
            self.assertEqual(self.assistant.history[1]["content"], "How are you?")
            self.assertEqual(self.assistant.history[2]["content"], "I am doing well, thank you!")
            mock_speak.assert_called_once_with("I am doing well, thank you!")


if __name__ == "__main__":
    unittest.main()
