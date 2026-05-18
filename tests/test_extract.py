from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from shazam_segments.extract import extract_clip


class ExtractTests(TestCase):
    def test_rejects_segment_outside_source_duration(self):
        with TemporaryDirectory() as temp:
            output = Path(temp) / "clip.mp3"
            with patch("shazam_segments.extract.require_ffmpeg"), patch(
                "shazam_segments.extract.audio_duration", return_value=5
            ):
                with self.assertRaisesRegex(ValueError, "outside the available audio preview"):
                    extract_clip("preview.mp3", 6, 2, output)

            self.assertFalse(output.exists())
