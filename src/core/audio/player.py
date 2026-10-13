"""Audio playback functionality with multi-backend support and safe resource cleanup."""

from __future__ import annotations

import io
import os
import sys
import time
from pathlib import Path
from typing import Union, Optional

from src.core.logger import logger
from src.core.config import config


class AudioPlayer:
    """Multi-backend audio player with proper resource release on Windows/POSIX."""

    def __init__(self, backend: Optional[str] = None):
        self.backend = (backend or config.playback_engine).lower()
        self._pygame_initialized = False

    def _ensure_pygame_init(self) -> bool:
        """Lazily initialize pygame mixer with safe error handling."""
        if self._pygame_initialized:
            return True
        try:
            import pygame
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._pygame_initialized = True
            return True
        except Exception as e:
            logger.warning(f"Could not initialize Pygame mixer: {e}")
            return False

    def play_with_pygame(self, source: Union[str, Path, io.BytesIO], block: bool = True) -> bool:
        """Play audio using pygame mixer with guaranteed file release.

        Args:
            source: File path or BytesIO buffer containing audio.
            block: If True, blocks until audio finishes playing.

        Returns:
            bool: True if playback completed successfully, False otherwise.
        """
        if not self._ensure_pygame_init():
            return False

        import pygame
        temp_file_created = False
        file_path: Optional[str] = None

        try:
            if isinstance(source, io.BytesIO):
                source.seek(0)
                try:
                    pygame.mixer.music.load(source)
                except Exception:
                    # Some versions of SDL_mixer need a physical file
                    temp_file = config.temp_dir / f"stream_{int(time.time() * 1000)}.mp3"
                    with open(temp_file, "wb") as f:
                        f.write(source.getvalue())
                    file_path = str(temp_file)
                    temp_file_created = True
                    pygame.mixer.music.load(file_path)
            else:
                file_path = str(source)
                if not Path(file_path).exists():
                    logger.error(f"Audio file not found: {file_path}")
                    return False
                pygame.mixer.music.load(file_path)

            pygame.mixer.music.play()
            logger.debug(f"Playback started using Pygame: {source}")

            if block:
                clock = pygame.time.Clock()
                while pygame.mixer.music.get_busy():
                    clock.tick(15)

            return True

        except Exception as e:
            logger.error(f"Pygame playback error: {e}")
            return False

        finally:
            try:
                # Crucial for Windows: stop and unload to release OS file handle
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
                    if hasattr(pygame.mixer.music, "unload"):
                        pygame.mixer.music.unload()
            except Exception as e:
                logger.debug(f"Error unloading pygame music: {e}")

            if temp_file_created and file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    pass

    def play_with_winsound(self, source: Union[str, Path]) -> bool:
        """Play audio using Windows native winsound (WAV format only)."""
        if sys.platform != "win32":
            return False
        try:
            import winsound
            file_path = str(source)
            if not os.path.exists(file_path):
                logger.error(f"Audio file not found: {file_path}")
                return False
            winsound.PlaySound(file_path, winsound.SND_FILENAME)
            return True
        except Exception as e:
            logger.warning(f"Winsound playback failed: {e}")
            return False

    def play_with_playsound(self, source: Union[str, Path]) -> bool:
        """Play audio using playsound library if available."""
        try:
            from playsound import playsound
            file_path = str(source)
            playsound(file_path)
            return True
        except ImportError:
            logger.warning("playsound package is not installed.")
            return False
        except Exception as e:
            logger.error(f"playsound playback failed: {e}")
            return False

    def play(self, source: Union[str, Path, io.BytesIO], block: bool = True) -> bool:
        """Automatically select and play audio through the best available backend.

        Args:
            source: Audio file path or BytesIO buffer.
            block: Whether to wait for playback to complete.

        Returns:
            bool: True if played successfully, False otherwise.
        """
        # If user explicitly requested winsound and source is a WAV file
        if self.backend == "winsound" and isinstance(source, (str, Path)) and str(source).endswith(".wav"):
            return self.play_with_winsound(source)

        # Pygame is preferred across all platforms
        if self.backend in ("auto", "pygame"):
            if self.play_with_pygame(source, block=block):
                return True

        # Fallback to winsound on Windows for WAV files
        if sys.platform == "win32" and isinstance(source, (str, Path)) and str(source).endswith(".wav"):
            logger.info("Falling back to winsound for WAV playback...")
            if self.play_with_winsound(source):
                return True

        # Fallback to playsound if installed
        if self.backend in ("auto", "playsound") and isinstance(source, (str, Path)):
            return self.play_with_playsound(source)

        logger.error(f"No functional audio player backend available to play {source}")
        return False


# Global player instance
player = AudioPlayer()


# Backwards compatibility helper functions
def play_with_pygame(filename: str) -> bool:
    """Play audio file using Pygame mixer."""
    return player.play_with_pygame(filename, block=True)


def play_with_playsound(filename: str) -> bool:
    """Play audio file using playsound."""
    return player.play_with_playsound(filename)


def play_audio(source: Union[str, Path, io.BytesIO], block: bool = True) -> bool:
    """Play audio through the default AudioPlayer."""
    return player.play(source, block=block)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        play_audio(sys.argv[1])
    else:
        print("Usage: python player.py <audio_file>")