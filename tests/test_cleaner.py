"""Unit tests for temporary file cleaner utility."""

import tempfile
import unittest
from pathlib import Path
from src.core.utils.temp_file_cleaner import clean_folder


class TestTempFileCleaner(unittest.TestCase):
    """Test folder cleanup operations."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        # Ensure test directory is removed
        if self.test_dir.exists():
            for f in self.test_dir.glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                self.test_dir.rmdir()
            except Exception:
                pass

    def test_clean_empty_folder(self):
        count = clean_folder(self.test_dir)
        self.assertEqual(count, 0)

    def test_clean_non_existent_folder(self):
        fake_path = self.test_dir / "does_not_exist_sub"
        count = clean_folder(fake_path)
        self.assertEqual(count, 0)

    def test_clean_files_with_pattern(self):
        # Create dummy mp3 and txt files
        (self.test_dir / "sample1.mp3").write_text("audio1")
        (self.test_dir / "sample2.mp3").write_text("audio2")
        (self.test_dir / "notes.txt").write_text("text")

        # Clean only *.mp3
        deleted = clean_folder(self.test_dir, pattern="*.mp3")
        self.assertEqual(deleted, 2)
        self.assertTrue((self.test_dir / "notes.txt").exists())
        self.assertFalse((self.test_dir / "sample1.mp3").exists())

    def test_clean_all_files(self):
        (self.test_dir / "sample.wav").write_text("audio")
        (self.test_dir / "sample.mp3").write_text("audio")

        deleted = clean_folder(self.test_dir)
        self.assertEqual(deleted, 2)
        remaining = list(self.test_dir.glob("*"))
        self.assertEqual(len(remaining), 0)


if __name__ == "__main__":
    unittest.main()
