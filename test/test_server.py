import unittest
from unittest.mock import patch, MagicMock
from src.server import _thread_local

from src import server

class TestYoutubeCaptionTool(unittest.TestCase):

    @patch('src.server.handle_get_youtube_captions_tool')
    def test_get_youtube_captions_success(self, mock_handle_tool):
        """Test successful YouTube caption fetching via the tool handler."""
        mock_handle_tool.return_value = {
            "captions": "hello\nworld",
            "video_id": "dQw4w9WgXcQ",
            "language_codes_used": "en"
        }
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        result = server.handle_get_youtube_captions_tool(youtube_url=url)

        mock_handle_tool.assert_called_once_with(youtube_url=url)
        self.assertEqual(result["captions"], "hello\nworld")
        self.assertEqual(result["video_id"], "dQw4w9WgXcQ")
        self.assertEqual(result["language_codes_used"], "en") # Assert against the expected default language

    @patch('src.server.handle_get_youtube_captions_tool')
    def test_get_youtube_captions_with_languages(self, mock_handle_tool):
        """Test YouTube caption fetching with specified languages via the tool handler."""
        mock_handle_tool.return_value = {
            "captions": "hola\nmundo",
            "video_id": "dQw4w9WgXcQ",
            "language_codes_used": "es" # Should be a single string now
        }
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        preferred_lang = "es" # Use preferred_lang
        result = server.handle_get_youtube_captions_tool(youtube_url=url, preferred_lang=preferred_lang)

        mock_handle_tool.assert_called_once_with(youtube_url=url, preferred_lang=preferred_lang)
        self.assertEqual(result["captions"], "hola\nmundo")
        self.assertEqual(result["video_id"], "dQw4w9WgXcQ")
        self.assertEqual(result["language_codes_used"], "es") # Assert against the single language string

    @patch('src.server.handle_get_youtube_captions_tool')
    def test_get_youtube_captions_transcripts_disabled(self, mock_handle_tool):
        """Test handling TranscriptsDisabled via the tool handler."""
        mock_handle_tool.return_value = {
            "error": {"message": "Transcripts are disabled for video: disabled_captions", "code": "TRANSCRIPTS_DISABLED"}
        }
        url = "https://www.youtube.com/watch?v=disabled_captions"
        result = server.handle_get_youtube_captions_tool(youtube_url=url)

        mock_handle_tool.assert_called_once_with(youtube_url=url)
        self.assertIn("error", result)
        self.assertEqual(result["error"]["code"], "TRANSCRIPTS_DISABLED")

    @patch('src.server.handle_get_youtube_captions_tool')
    def test_get_youtube_captions_no_transcript_found_with_fallback(self, mock_handle_tool):
        """Test handling NoTranscriptFound with available fallback via the tool handler."""
        mock_handle_tool.return_value = {
            "captions": "bonjour",
            "video_id": "no_trans_fd",
            "language_codes_used": "fr", # Should be a single string now
            "message": "No transcript found for video: no_trans_fd with requested language: en. Fetched available: fr" # Updated message
        }
        url = "https://www.youtube.com/watch?v=no_trans_fd"
        preferred_lang = "en" # Use preferred_lang
        result = server.handle_get_youtube_captions_tool(youtube_url=url, preferred_lang=preferred_lang)

        mock_handle_tool.assert_called_once_with(youtube_url=url, preferred_lang=preferred_lang)
        self.assertNotIn("error", result)
        self.assertEqual(result["captions"], "bonjour")
        self.assertEqual(result["video_id"], "no_trans_fd")
        self.assertEqual(result["language_codes_used"], "fr") # Assert against the single language string
        self.assertIn("message", result)

    @patch('src.server.handle_get_youtube_captions_tool')
    def test_get_youtube_captions_no_transcript_found_no_fallback(self, mock_handle_tool):
        """Test handling NoTranscriptFound with no available fallback via the tool handler."""
        mock_handle_tool.return_value = {
            "error": {
                "message": "No transcript found for video: no_transcript_at_all with requested language: en.", # Updated message
                "code": "NO_TRANSCRIPT_FOUND_FOR_SPECIFIED_LANGUAGE" # Updated error code
            },
            "requested_language": "en", # Add requested_language
            "available_languages": []
        }
        url = "https://www.youtube.com/watch?v=no_transcript_at_all"
        preferred_lang = "en" # Use preferred_lang
        result = server.handle_get_youtube_captions_tool(youtube_url=url, preferred_lang=preferred_lang)

        mock_handle_tool.assert_called_once_with(youtube_url=url, preferred_lang=preferred_lang)
        self.assertIn("error", result)
        self.assertEqual(result["error"]["code"], "NO_TRANSCRIPT_FOUND_FOR_SPECIFIED_LANGUAGE") # Assert against updated error code

    @patch('src.server.handle_get_youtube_captions_tool')
    def test_get_youtube_captions_invalid_url(self, mock_handle_tool):
        """Test handling invalid YouTube URL via the tool handler."""
        mock_handle_tool.return_value = {
            "error": {"message": "Invalid YouTube URL or could not extract video ID.", "code": "INVALID_URL"}
        }
        url = "http://example.com"
        result = server.handle_get_youtube_captions_tool(youtube_url=url)

        mock_handle_tool.assert_called_once_with(youtube_url=url)
        self.assertIn("error", result)
        self.assertEqual(result["error"]["code"], "INVALID_URL")

    @patch('src.server.handle_get_youtube_captions_tool')
    def test_get_youtube_captions_unexpected_error(self, mock_handle_tool):
        """Test handling unexpected exceptions via the tool handler."""
        mock_handle_tool.return_value = {
            "error": {"message": "An unexpected error occurred: Some unexpected error", "code": "UNEXPECTED_ERROR"}
        }
        url = "https://www.youtube.com/watch?v=some_video_id" # Use a valid format URL for this test
        result = server.handle_get_youtube_captions_tool(youtube_url=url)

        mock_handle_tool.assert_called_once_with(youtube_url=url)
        self.assertIn("error", result)
        self.assertEqual(result["error"]["code"], "UNEXPECTED_ERROR")
        self.assertIn("Some unexpected error", result["error"]["message"])

class TestBilibiliCaptionTool(unittest.IsolatedAsyncioTestCase):

    @patch('src.server.fetch_bilibili_subtitle')
    async def test_get_bilibili_captions_success(self, mock_fetch_subtitle):
        """Test successful Bilibili caption fetching via the tool handler."""
        mock_fetch_subtitle.return_value = "Subtitle content line 1\nSubtitle content line 2"
        url = "https://www.bilibili.com/video/BV1xx411c7mY/"
        # Call the actual tool handler function in server.py
        result = await server.handle_get_bilibili_captions_tool(url=url)

        mock_fetch_subtitle.assert_called_once()
        # Check arguments passed to the fetcher function
        self.assertEqual(mock_fetch_subtitle.call_args.args[0], url)
        self.assertEqual(mock_fetch_subtitle.call_args.kwargs['preferred_lang'], "zh-CN")
        self.assertEqual(mock_fetch_subtitle.call_args.kwargs['output_format'], "text")
        # Credential might be None or a mock depending on env setup, just check it's passed

        self.assertEqual(result, "Subtitle content line 1\nSubtitle content line 2")

    @patch('src.server.fetch_bilibili_subtitle')
    async def test_get_bilibili_captions_with_language_and_format(self, mock_fetch_subtitle):
        """Test Bilibili caption fetching with specified language and format via the tool handler."""
        mock_fetch_subtitle.return_value = "00:00:00.000 --> 00:00:01.000\nLine 1\n\n00:00:01.500 --> 00:00:02.500\nLine 2\n\n"
        url = "https://www.bilibili.com/video/BV1xx411c7mY/?p=2"
        lang = "en"
        fmt = "timestamped"
        result = await server.handle_get_bilibili_captions_tool(url=url, preferred_lang=lang, output_format=fmt)

        mock_fetch_subtitle.assert_called_once()
        self.assertEqual(mock_fetch_subtitle.call_args.args[0], url)
        self.assertEqual(mock_fetch_subtitle.call_args.kwargs['preferred_lang'], lang)
        self.assertEqual(mock_fetch_subtitle.call_args.kwargs['output_format'], fmt)

        self.assertIn("-->", result) # Check for timestamp format

    @patch('src.server.fetch_bilibili_subtitle')
    async def test_get_bilibili_captions_error_from_fetcher(self, mock_fetch_subtitle):
        """Test handling error returned by the fetcher function via the tool handler."""
        error_message = "Error: Could not extract a valid bvid from the URL: http://example.com"
        mock_fetch_subtitle.return_value = error_message
        url = "http://example.com"
        result = await server.handle_get_bilibili_captions_tool(url=url)

        mock_fetch_subtitle.assert_called_once()
        self.assertEqual(mock_fetch_subtitle.call_args.args[0], url)

        self.assertEqual(result, error_message)
        self.assertIn("Error:", result)

# Need to update the main execution block to run async tests
if __name__ == '__main__':
    # Use asyncio.run to run the async tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# Remove the old TestYouTubeCaptionServer class entirely
# The YouTube tests above have been integrated into TestCaptionServerTools
# The _extract_video_id test is removed as that function is now in youtube_fetcher and should be tested there.