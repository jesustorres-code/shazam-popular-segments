import unittest

from shazam_segments.screenshot import parse_segment_text


class ScreenshotTests(unittest.TestCase):
    def test_parse_segment_text(self):
        segment = parse_segment_text("Most Popular\nPast 7 Days\n00:00 - 00:05")
        self.assertIsNotNone(segment)
        self.assertEqual(segment["start"], "00:00")
        self.assertEqual(segment["end"], "00:05")
        self.assertEqual(segment["durationSeconds"], 5)

    def test_parse_segment_text_rejects_missing_range(self):
        self.assertIsNone(parse_segment_text("Most Popular"))


if __name__ == "__main__":
    unittest.main()
