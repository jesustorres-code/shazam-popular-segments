import unittest

from shazam_segments.cases import build_case, popular_segment, query_from_shazam_url, shazam_track_id_from_url, slugify
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

    def test_slugify(self):
        self.assertEqual(slugify("EL DE LA TINTA - holanda"), "el-de-la-tinta-holanda")

    def test_build_case_with_segment(self):
        case = build_case(
            {"provider": "deezer", "title": "holanda", "artist": "EL DE LA TINTA", "durationSeconds": 224},
            "holanda",
            segment_start="00:00",
            segment_end="00:05",
            shazam_url="https://www.shazam.com/track/example",
        )
        self.assertEqual(case["shazamPopularSegment"]["startSeconds"], 0)
        self.assertEqual(case["shazamPopularSegment"]["endSeconds"], 5)
        self.assertEqual(case["shazamUrl"], "https://www.shazam.com/track/example")

    def test_query_from_shazam_url(self):
        self.assertEqual(
            query_from_shazam_url("https://www.shazam.com/song/1471572221/smack-that-feat-eminem?referrer=browserextension"),
            "smack that feat eminem",
        )

    def test_shazam_track_id_from_url(self):
        self.assertEqual(
            shazam_track_id_from_url("https://www.shazam.com/song/1443123583/go"),
            1443123583,
        )


if __name__ == "__main__":
    unittest.main()
