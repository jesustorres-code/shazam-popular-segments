from unittest import TestCase

from shazam_segments.metadata import compose_youtube_music_query, cookie_jar_from_text, youtube_video_id_from_url


class MetadataTests(TestCase):
    def test_compose_youtube_music_query_cleans_topic_and_video_suffix(self):
        query = compose_youtube_music_query("Go (Official Video)", "The Chemical Brothers - Topic")
        self.assertEqual(query, "The Chemical Brothers Go")

    def test_compose_youtube_music_query_removes_repeated_artist_prefix(self):
        query = compose_youtube_music_query("Rick Astley - Never Gonna Give You Up (Official Video)", "Rick Astley")
        self.assertEqual(query, "Rick Astley Never Gonna Give You Up")

    def test_compose_youtube_music_query_cleans_spanish_video_suffix_and_repeated_artist(self):
        query = compose_youtube_music_query(
            "Juan Freer x Legion RG - Los Sueños Se Trabajan [Video Oficial]",
            "Juan Freer",
        )
        self.assertEqual(query, "Juan Freer Legion RG - Los Sueños Se Trabajan")

    def test_cookie_jar_from_raw_cookie_header(self):
        jar = cookie_jar_from_text("Cookie: SID=abc; HSID=def")
        names = sorted(cookie.name for cookie in jar)
        self.assertEqual(names, ["HSID", "HSID", "SID", "SID"])

    def test_cookie_jar_from_netscape_cookie_text(self):
        jar = cookie_jar_from_text(".youtube.com\tTRUE\t/\tTRUE\t1893456000\tSID\tabc")
        cookies = list(jar)
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookies[0].name, "SID")
        self.assertEqual(cookies[0].value, "abc")

    def test_cookie_jar_from_browser_json_export(self):
        jar = cookie_jar_from_text(
            '[{"domain":".youtube.com","expirationDate":1893456000.1,"name":"SID","path":"/","secure":true,"value":"abc"}]'
        )
        cookies = list(jar)
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookies[0].domain, ".youtube.com")
        self.assertEqual(cookies[0].name, "SID")
        self.assertEqual(cookies[0].expires, 1893456000)

    def test_youtube_video_id_from_url(self):
        self.assertEqual(youtube_video_id_from_url("https://music.youtube.com/watch?v=rOC4rMWFnOo&si=x"), "rOC4rMWFnOo")
        self.assertEqual(youtube_video_id_from_url("https://youtu.be/rOC4rMWFnOo"), "rOC4rMWFnOo")
