import unittest

from shazam_segments.cases import popular_segment
from shazam_segments.timecode import duration_from_range, format_seconds, parse_timecode


class TimecodeTests(unittest.TestCase):
    def test_parse_seconds(self):
        self.assertEqual(parse_timecode("7"), 7)
        self.assertEqual(parse_timecode(7), 7)

    def test_parse_mmss(self):
        self.assertEqual(parse_timecode("03:44"), 224)

    def test_parse_hhmmss(self):
        self.assertEqual(parse_timecode("01:02:03"), 3723)

    def test_duration_from_range(self):
        self.assertEqual(duration_from_range("00:00", "00:05"), 5)

    def test_format_seconds(self):
        self.assertEqual(format_seconds(224), "03:44")

    def test_popular_segment(self):
        case = {"shazamPopularSegment": {"start": "00:00", "end": "00:05"}}
        segment = popular_segment(case)
        self.assertEqual(segment.start, 0)
        self.assertEqual(segment.duration, 5)

    def test_video_override(self):
        case = {"shazamPopularSegment": {"start": "00:00", "end": "00:05"}}
        segment = popular_segment(case, video_seconds=7)
        self.assertEqual(segment.start, 0)
        self.assertEqual(segment.duration, 7)


if __name__ == "__main__":
    unittest.main()
