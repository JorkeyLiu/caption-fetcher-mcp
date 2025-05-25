import re
import re
import logging
from typing import Optional, Dict, Any
import time # Import time for retry delay

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

# Get module-level logger
logger = logging.getLogger(__name__)

# Constants for retry logic
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

# Helper function to extract video ID
def extract_youtube_video_id(youtube_url: str) -> Optional[str]:
    """
    Extracts YouTube video ID from various URL formats using a single regex.
    Supports watch?v=, embed/, v/, shorts/ formats on youtube.com (with/without www/m subdomains) and youtu.be/.
    """
    logger.debug(f"Attempting to extract video ID from: {youtube_url}")

    # Regex for various YouTube URL formats
    patterns = [
        r'(?:https?:\/\/)?(?:(?:www\.|m\.)?youtube\.com\/(?:watch\?v=|embed\/|v\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            video_id = match.group(1)
            logger.debug(f"Extracted video ID using regex: {video_id}")
            return video_id

    logger.warning(f"Could not extract video ID from URL: {youtube_url}")
    return None

def fetch_youtube_captions(
    youtube_url: str,
    preferred_lang: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetches captions for a given YouTube video URL.

    :param youtube_url: The URL of the YouTube video.
    :param preferred_lang: Optional preferred language code (e.g., 'en').
    :return: A dictionary containing captions, video_id, and language_codes_used, or an error dictionary.
    """
    logger.info(f"Received request for URL: {youtube_url} with preferred language: {preferred_lang}")

    video_id = extract_youtube_video_id(youtube_url)
    if not video_id:
        error_msg = "Invalid YouTube URL or could not extract video ID."
        logger.error(f"Failed to extract video ID from URL: {youtube_url}")
        return {"error": {"message": error_msg, "code": "INVALID_URL"}}

    try:
        logger.info(f"Fetching transcript for video ID: {video_id} with preferred language: {preferred_lang}")

        if not preferred_lang: # Default behavior: use ASR language for priority
            logger.info(f"No preferred language specified. Attempting to find suitable transcript based on ASR language for video ID: {video_id}")
            try:
                transcript_options = YouTubeTranscriptApi.list_transcripts(video_id)

                # Find the original video language from ASR transcripts
                asr_transcripts = [t for t in transcript_options if t.is_generated]
                original_video_lang = None
                if asr_transcripts:
                    original_video_lang = asr_transcripts[0].language_code
                    logger.info(f"Inferred original video language from ASR: {original_video_lang}")

                chosen_transcript = None
                if original_video_lang:
                    # Prioritize manually created (CC) transcripts in the original video language
                    matching_cc_transcripts = [t for t in transcript_options if not t.is_generated and t.language_code == original_video_lang]
                    if matching_cc_transcripts:
                        chosen_transcript = matching_cc_transcripts[0] # Pick the first matching CC transcript
                        logger.info(f"Selected manually created transcript in original video language: {chosen_transcript.language_code}")
                    else:
                        # If no matching CC transcript, use the ASR transcript in the original video language
                        chosen_transcript = asr_transcripts[0] # This should exist if original_video_lang was determined
                        logger.info(f"No matching CC transcript found. Selected ASR transcript in original video language: {chosen_transcript.language_code}")
                else:
                    # Fallback if no ASR transcripts are available (cannot determine original language)
                    logger.warning(f"No ASR transcripts found for video ID: {video_id}. Falling back to general priority.")
                    # Fallback logic: Prioritize 'en' CC, then first available CC, then 'en' ASR, then first available ASR
                    cc_transcripts = [t for t in transcript_options if not t.is_generated]
                    asr_transcripts_fallback = [t for t in transcript_options if t.is_generated] # Re-filter ASR for fallback

                    en_cc = next((t for t in cc_transcripts if t.language_code == 'en'), None)
                    if en_cc:
                        chosen_transcript = en_cc
                        logger.info(f"Fallback: Selected 'en' manually created transcript.")
                    elif cc_transcripts:
                        chosen_transcript = cc_transcripts[0]
                        logger.info(f"Fallback: Selected first available manually created transcript: {chosen_transcript.language_code}")
                    else:
                        en_asr = next((t for t in asr_transcripts_fallback if t.language_code == 'en'), None)
                        if en_asr:
                            chosen_transcript = en_asr
                            logger.info(f"Fallback: Selected 'en' auto-generated transcript.")
                        elif asr_transcripts_fallback:
                            chosen_transcript = asr_transcripts_fallback[0]
                            logger.info(f"Fallback: Selected first available auto-generated transcript: {chosen_transcript.language_code}")


                if chosen_transcript:
                    for attempt in range(MAX_RETRIES):
                        try:
                            transcript_list = chosen_transcript.fetch()
                            languages_used = chosen_transcript.language_code # Use single string
                            logger.info(f"Successfully fetched transcript for video ID: {video_id} with language: {languages_used} on attempt {attempt + 1}")

                            captions = "\n".join([item.text for item in transcript_list])
                            return {"captions": captions, "video_id": video_id, "language_codes_used": languages_used}
                        except Exception as e:
                            if attempt < MAX_RETRIES - 1:
                                logger.warning(f"Attempt {attempt + 1} failed for video ID {video_id}: {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
                                time.sleep(RETRY_DELAY_SECONDS)
                            else:
                                logger.error(f"Failed to fetch transcript for video ID {video_id} after {MAX_RETRIES} attempts: {e}")
                                raise e # Re-raise the exception to be caught by the outer handler
                else:
                     # No usable transcripts found even after fallback
                     warning_msg = f"No usable transcripts found for video: {video_id} after checking ASR language and fallback options."
                     logger.warning(warning_msg)
                     return {
                         "error": {
                             "message": warning_msg,
                             "code": "NO_USABLE_TRANSCRIPT_FOUND"
                         },
                         "available_languages": [t.language_code for t in transcript_options] if transcript_options else []
                     }

            except TranscriptsDisabled:
                warning_msg = f"Transcripts are disabled for video: {video_id}"
                logger.warning(warning_msg)
                return {"error": {"message": warning_msg, "code": "TRANSCRIPTS_DISABLED"}}
            except NoTranscriptFound:
                 # This might occur if list_transcripts finds a track but fetch() fails,
                 # or if list_transcripts itself returns an empty list (less likely with the above logic).
                 warning_msg = f"No transcript found for video: {video_id} during default fetch attempt."
                 logger.warning(warning_msg)
                 return {
                     "error": {
                         "message": warning_msg,
                         "code": "NO_TRANSCRIPT_FOUND_DEFAULT"
                     }
                 }
            except Exception as e_default:
                 error_msg = f"An error occurred during default transcript fetching for video ID {video_id}: {str(e_default)}"
                 logger.error(error_msg)
                 return {"error": {"message": error_msg, "code": "DEFAULT_FETCH_ERROR"}}

        else: # Try specified language code
            logger.info(f"Fetching transcript for video ID: {video_id} with specified language: {preferred_lang}")
            try:
                # Use find_transcript to get a single transcript for the preferred language
                transcript = YouTubeTranscriptApi.list_transcripts(video_id).find_transcript([preferred_lang])
                for attempt in range(MAX_RETRIES):
                    try:
                        transcript_list = transcript.fetch()
                        languages_used = preferred_lang # Use single string
                        logger.info(f"Successfully fetched transcript for video ID: {video_id} with language: {languages_used} on attempt {attempt + 1}")

                        captions = "\n".join([item.text for item in transcript_list])
                        return {"captions": captions, "video_id": video_id, "language_codes_used": languages_used}
                    except Exception as e:
                        if attempt < MAX_RETRIES - 1:
                            logger.warning(f"Attempt {attempt + 1} failed for video ID {video_id} with language {preferred_lang}: {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
                            time.sleep(RETRY_DELAY_SECONDS)
                        else:
                            logger.error(f"Failed to fetch transcript for video ID {video_id} with language {preferred_lang} after {MAX_RETRIES} attempts: {e}")
                            raise e # Re-raise the exception to be caught by the outer handler

            except TranscriptsDisabled:
                warning_msg = f"Transcripts are disabled for video: {video_id}"
                logger.warning(warning_msg)
                return {"error": {"message": warning_msg, "code": "TRANSCRIPTS_DISABLED"}}
            except NoTranscriptFound:
                warning_msg = f"No transcript found for video: {video_id} with requested language: {preferred_lang}."
                logger.warning(warning_msg)
                # In this case, the user requested a specific language and it wasn't found.
                # We should return an error indicating this, possibly listing available languages.
                available_transcripts = []
                try:
                     transcript_options = YouTubeTranscriptApi.list_transcripts(video_id)
                     available_transcripts = [t.language_code for t in transcript_options]
                     logger.info(f"Available transcripts for video ID {video_id}: {available_transcripts}")
                except Exception as e_list:
                     logger.error(f"Error listing transcripts during NoTranscriptFound handling for video {video_id}: {str(e_list)}")
                     # Continue without available languages list if listing fails

                return {
                    "error": {
                        "message": warning_msg,
                        "code": "NO_TRANSCRIPT_FOUND_FOR_SPECIFIED_LANGUAGE"
                    },
                    "requested_language": preferred_lang,
                    "available_languages": available_transcripts if available_transcripts else "Could not retrieve available languages."
                }
            except Exception as e_specified:
                error_msg = f"An error occurred while fetching transcript for specified language {preferred_lang} for video ID {video_id}: {str(e_specified)}"
                logger.error(error_msg)
                return {"error": {"message": error_msg, "code": "SPECIFIED_FETCH_ERROR"}}

    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        logger.error(f"An unexpected error occurred for video ID {video_id}: {str(e)}")
        return {"error": {"message": error_msg, "code": "UNEXPECTED_ERROR"}}