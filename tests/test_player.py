"""Unit tests for audio player."""

import io
import unittest
from unittest.mock import patch, MagicMock
from src.core.audio.player import AudioPlayer


class TestAudioPlayer(unittest.TestCase):
    """Test audio player backend dispatch and safety."""

    def setUp(self):
        self.player = AudioPlayer(backend="auto")

    def test_play_non_existent_file(self):
        result = self.player.play("non_existent_file_12345.mp3")
        self.assertFalse(result)

    @patch("src.core.audio.player.AudioPlayer.play_with_pygame")
    def test_play_delegates_to_pygame(self, mock_play_pygame):
        mock_play_pygame.return_value = True
        fake_buffer = io.BytesIO(b"RIFFdummydata")
        success = self.player.play(fake_buffer)
        self.assertTrue(success)
        mock_play_pygame.assert_called_once_with(fake_buffer, block=True)

    @patch("src.core.audio.player.AudioPlayer.play_with_pygame")
    @patch("src.core.audio.player.AudioPlayer.play_with_winsound")
    def test_play_wav_fallback(self, mock_play_winsound, mock_play_pygame):
        mock_play_pygame.return_value = False
        mock_play_winsound.return_value = True

        player = AudioPlayer(backend="auto")
        with patch("sys.platform", "win32"):
            success = player.play("test.wav")
            self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
