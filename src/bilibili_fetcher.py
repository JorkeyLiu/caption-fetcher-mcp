import os
import re
import httpx
import os
import re
import httpx
import logging
from typing import Optional, Literal
from urllib.parse import urlparse, parse_qs

from bilibili_api import video, Credential
from bilibili_api.utils.network import ResponseCodeException

# Get module-level logger
logger = logging.getLogger(__name__)

# Helper function to parse Bilibili URL
def parse_bilibili_url(url: str) -> tuple[Optional[str], Optional[int]]:
    """
    Parses a Bilibili video URL to extract bvid and page number.
    Handles URLs like:
    - https://www.bilibili.com/video/BVxxxxxxxxxx/
    - https://www.bilibili.com/video/BVxxxxxxxxxx?p=2
    - https://m.bilibili.com/video/BVxxxxxxxxxx
    - https://m.bilibili.com/video/BVxxxxxxxxxx?p=3
    """
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split("/")
    bvid = None
    page = None

    # Find BV ID in path
    for part in path_parts:
        if re.match(r"^BV[1-9A-HJ-NP-Za-km-z]{10}$", part):
            bvid = part
            break

    # Find page number in query parameters
    query_params = parse_qs(parsed_url.query)
    if "p" in query_params:
        try:
            page = int(query_params["p"][0])
        except (ValueError, IndexError):
            pass  # Ignore invalid page numbers

    return bvid, page

async def fetch_bilibili_subtitle(
    url: str,
    credential: Optional[Credential] = None,
    preferred_lang: str = "zh-CN",
    output_format: Literal["text", "timestamped"] = "text",
) -> str:
    """
    Fetches subtitles for a given Bilibili video URL.

    :param url: The URL of the Bilibili video (e.g., "https://www.bilibili.com/video/BV1fz4y1j7Mf/?p=2").
    :param credential: Bilibili Credential object. Can be None if not needed for public videos.
    :param preferred_lang: The preferred subtitle language code (e.g., 'zh-CN', 'ai-zh', 'en'). Defaults to 'zh-CN'.
                           Check the video page for available languages. 'ai-zh' is often AI-generated Chinese.
    :param output_format: The desired format for the subtitles ('text' for plain text, 'timestamped' for text with timestamps). Defaults to 'text'.
    :return: The formatted subtitle string, or an error message.
    """
    logger.info(
        f"Received request for URL: {url}, lang: {preferred_lang}, format: {output_format}"
    )

    bvid, page = parse_bilibili_url(url)

    if not bvid:
        error_msg = f"Error: Could not extract a valid bvid from the URL: {url}"
        logger.error(error_msg)
        return error_msg

    logger.info(f"Parsed bvid: {bvid}, page: {page}")

    try:
        # Check for sessdata in environment variables
        env_sessdata = os.environ.get("SESSDATA")
        env_bili_jct = os.environ.get("BILI_JCT")
        env_buvid3 = os.environ.get("BUVID3")

        determined_credential = credential # Start with the passed credential

        if env_sessdata:
            logger.info("Using sessdata from environment variable SESSDATA")
            # Prioritize environment variables if sessdata is provided
            determined_credential = Credential(
                sessdata=env_sessdata,
                bili_jct=env_bili_jct,
                buvid3=env_buvid3
            )
        elif (env_bili_jct or env_buvid3):
             logger.warning("SESSDATA environment variable is not set, but BILI_JCT or BUVID3 are. SESSDATA is required for credential.")


        v = video.Video(bvid=bvid, credential=determined_credential)

        # Get video info to find the correct cid
        info = await v.get_info()
        logger.debug(f"Video info fetched for {bvid}")

        cid: Optional[int] = None
        # Check if 'pages' key exists and is a list before accessing it
        pages_info = info.get("pages")
        if page and isinstance(pages_info, list) and len(pages_info) >= page:
            # Check if page number is valid (page is 1-based index)
            if 0 < page <= len(pages_info):
                cid = pages_info[page - 1].get("cid")  # Use .get for safety
                if cid:
                    logger.info(f"Found cid {cid} for page {page}")
                else:
                     logger.warning(
                        f"Page {page} found in 'pages' list, but 'cid' key is missing for that page."
                    )
                     # Fallback to default cid if specific page cid is missing
                     cid = info.get("cid")
            else:
                logger.warning(
                    f"Invalid page number {page} for video with {len(pages_info)} pages. Falling back to default page."
                )
                cid = info.get(
                    "cid"
                )  # Fallback to the default cid if page is out of range
        else:
            if page:
                logger.warning(
                    f"Page {page} requested but video seems to be single-part or page info missing/invalid. Using default cid."
                )
            cid = info.get(
                "cid"
            )  # Default cid for single-part videos or if page not specified/found
            if cid:
                logger.info(f"Using default cid {cid}")


        if not cid:
            error_msg = "Error: Could not determine the video part (CID)."
            logger.error(error_msg)
            return error_msg

        # Get available subtitles metadata
        subtitle_info = await v.get_subtitle(cid=cid)
        logger.debug(f"Subtitle metadata fetched: {subtitle_info}")

        available_subtitles = subtitle_info.get("subtitles", [])
        if not available_subtitles:
            info_msg = "Info: No subtitles found for this video part. This might be due to invalid or expired Bilibili credentials. Please check your SESSDATA and BILI_JCT environment variables."
            logger.warning(info_msg)
            return info_msg

        # Find the preferred subtitle URL
        subtitle_url: Optional[str] = None
        found_lang: Optional[str] = None

        # Prioritize exact match for preferred language
        for sub in available_subtitles:
            if sub.get("lan") == preferred_lang:
                subtitle_url = sub.get("subtitle_url")
                found_lang = sub.get("lan")
                logger.info(f"Found exact match for preferred language: {found_lang}")
                break

        # If exact match not found, try finding *any* subtitle (prioritizing non-AI)
        if not subtitle_url:
            logger.warning(
                f"Preferred language '{preferred_lang}' not found. Searching for alternatives."
            )
            # Try non-AI first
            for sub in available_subtitles:
                # Check if 'ai_type' exists and is 0 (manual/official) or if 'ai_type' doesn't exist
                is_manual = sub.get("ai_type", 0) == 0
                if is_manual:
                    subtitle_url = sub.get("subtitle_url")
                    found_lang = sub.get("lan")
                    logger.info(f"Found alternative non-AI subtitle: {found_lang}")
                    break
            # If still no subtitle found, take the first available AI one
            if not subtitle_url and available_subtitles:
                subtitle_url = available_subtitles[0].get("subtitle_url")
                found_lang = available_subtitles[0].get("lan")
                logger.info(f"Found first available AI subtitle: {found_lang}")


        if not subtitle_url:
            error_msg = "Error: Could not find any subtitle URL."
            logger.error(error_msg)
            return error_msg

        # Ensure URL starts with http: or https:
        if subtitle_url.startswith("//"):
            subtitle_url = "https:" + subtitle_url
        elif not subtitle_url.startswith(("http:", "https:")):
            error_msg = f"Error: Invalid subtitle URL format: {subtitle_url}"
            logger.error(error_msg)
            return error_msg

        logger.info(
            f"Fetching subtitle content from: {subtitle_url} (Language: {found_lang})"
        )

        # Fetch the actual subtitle JSON content
        async with httpx.AsyncClient() as client:
            # Add headers to mimic browser request, might help avoid blocks
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": f"https://www.bilibili.com/video/{bvid}/",  # Add referer
            }
            response = await client.get(
                subtitle_url, headers=headers, follow_redirects=True
            )
            response.raise_for_status()  # Raise an exception for bad status codes
            subtitle_data = response.json()
            logger.debug("Subtitle JSON data fetched successfully.")

        # Format the subtitle content
        body = subtitle_data.get("body", [])
        if not body:
            info_msg = "Info: Subtitle file fetched but contains no content."
            logger.warning(info_msg)
            return info_msg

        formatted_subtitle = ""
        if output_format == "timestamped":
            for item in body:
                start = item.get("from", 0.0)
                end = item.get("to", 0.0)
                content = item.get("content", "")
                # Simple timestamp format HH:MM:SS.ms
                start_h, start_rem = divmod(start, 3600)
                start_m, start_s = divmod(start_rem, 60)
                start_ms = int((start_s - int(start_s)) * 1000)

                end_h, end_rem = divmod(end, 3600)
                end_m, end_s = divmod(end_rem, 60)
                end_ms = int((end_s - int(end_s)) * 1000)

                formatted_subtitle += f"{int(start_h):02}:{int(start_m):02}:{int(start_s):02}.{start_ms:03} --> "
                formatted_subtitle += (
                    f"{int(end_h):02}:{int(end_m):02}:{int(end_s):02}.{end_ms:03}\n"
                )
                formatted_subtitle += f"{content}\n\n"
            logger.info("Formatted subtitles with timestamps.")
        else:  # Default to plain text
            lines = [item.get("content", "") for item in body]
            formatted_subtitle = "\n".join(lines)
            logger.info("Formatted subtitles as plain text.")

        return formatted_subtitle.strip()

    except httpx.HTTPStatusError as e:
        error_msg = (
            f"HTTP error fetching subtitle content: {e.response.status_code} for URL {e.request.url}"
        )
        logger.error(error_msg)
        # Provide more context in the error message
        error_details = f"HTTP Status {e.response.status_code}"
        try:
            # Try to get error details from response if available (might be HTML or JSON)
            error_body = e.response.text
            error_details += f" - Response: {error_body[:200]}"  # Limit response length
        except Exception:
            pass  # Ignore if response body cannot be read
        return f"Error fetching subtitle content: {error_details}"
    except httpx.RequestError as e:
        error_msg = f"Network error fetching subtitle content for URL {e.request.url}: {e}"
        logger.error(error_msg)
        return f"Error fetching subtitle content (network issue): {e}"
    except ResponseCodeException as e:
        # Access message via args[1] based on traceback
        api_error_message = e.args[1] if len(e.args) > 1 else str(e)
        error_msg = f"Bilibili API returned error code: {e.code}, message: {api_error_message}"
        logger.error(error_msg, exc_info=True) # Log full traceback

        # Check for specific error codes/messages
        if e.code == -404 and ("啥都木有" in api_error_message or "not found" in api_error_message.lower() or "access denied" in api_error_message.lower()):
            # Assuming -404 with "啥都木有" or "not found" indicates video not found
            return f"Error: Video with bvid '{bvid}' not found or access denied."
        else:
            # For other ResponseCodeExceptions, return a generic API error message
            return f"Error: Bilibili API error: {api_error_message} (Code: {e.code})"

    except Exception as e:
        error_msg = f"An unexpected error occurred: {type(e).__name__} - {e}"
        logger.error(f"An unexpected error occurred: {e}", exc_info=True) # Log full traceback

        # Fallback to generic unexpected error
        return error_msg