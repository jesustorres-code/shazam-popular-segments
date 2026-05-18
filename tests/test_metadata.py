from unittest import TestCase

from shazam_segments.metadata import compose_youtube_music_query


class MetadataTests(TestCase):
    def test_compose_youtube_music_query_cleans_topic_and_video_suffix(self):
        query = compose_youtube_music_query("Go (Official Video)", "The Chemical Brothers - Topic")
        self.assertEqual(query, "The Chemical Brothers Go")

    def test_compose_youtube_music_query_removes_repeated_artist_prefix(self):
        query = compose_youtube_music_query("Rick Astley - Never Gonna Give You Up (Official Video)", "Rick Astley")
        self.assertEqual(query, "Rick Astley Never Gonna Give You Up")
