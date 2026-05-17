import tempfile
import unittest
from pathlib import Path

from shazam_segments.workflow import extract_case, list_cases, list_clips


class WorkflowTests(unittest.TestCase):
    def test_extract_case_requires_audio_without_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            case_path = Path(temp) / "case" / "metadata.json"
            case_path.parent.mkdir()
            case_path.write_text(
                '{"shazamPopularSegment":{"start":"00:00","end":"00:05"}}\n',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                extract_case(case_path)

    def test_list_cases_empty_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(list_cases(Path(temp) / "missing"), [])

    def test_list_clips_empty_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(list_clips(Path(temp) / "missing"), [])


if __name__ == "__main__":
    unittest.main()
