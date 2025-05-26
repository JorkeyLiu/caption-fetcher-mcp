# MCP Server for YouTube Captions

import re
import logging # Import logging module
import threading

from mcp.server.fastmcp import FastMCP
import os # Import os for environment variables
from typing import Literal, Optional # Import Literal and Optional

from bilibili_api import Credential # Import Credential

from youtube_fetcher import fetch_youtube_captions # Import YouTube fetcher function
from bilibili_fetcher import fetch_bilibili_subtitle # Import Bilibili fetcher function

_thread_local = threading.local()

class TestMethodFilter(logging.Filter):
    """Custom filter to add test method name to log records."""
    def filter(self, record):
        record.test_method = getattr(_thread_local, 'test_method_name', 'N/A')
        return True

# Configure basic logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Get the root logger and add the custom filter
root_logger = logging.getLogger()
test_method_filter = TestMethodFilter()
root_logger.addFilter(test_method_filter)

# MCP Server class using FastMCP
# Create a module-level FastMCP instance
mcp = FastMCP(server_name="caption_fetcher_mcp", port=3521, host="0.0.0.0")
logging.info("MCP Server instance created.")

# MCP Server class using FastMCP
# Your Bilibili Credentials
# Get credentials from environment variables
@mcp.tool(
    name="get_youtube_captions",
    description="Fetches captions for a given YouTube video URL.",
)
def handle_get_youtube_captions_tool(youtube_url: str, preferred_lang: Optional[str] = None):
    """
    Handles the request to get YouTube captions by calling the youtube_fetcher module.
    """
    # Pass the logger instance to the fetcher function
    return fetch_youtube_captions(youtube_url, preferred_lang=preferred_lang)


@mcp.tool(
    name="get_bilibili_captions",
    description="Fetches captions for a given Bilibili video URL.",
)
async def handle_get_bilibili_captions_tool(
    url: str,
    preferred_lang: str = "zh-CN",
    output_format: Literal["text", "timestamped"] = "text",
):
    """
    Fetches subtitles for a given Bilibili video URL by calling the bilibili_fetcher module.
    """
    # Pass credentials and logger to the fetcher function
    return await fetch_bilibili_subtitle(
        url,
        preferred_lang=preferred_lang,
        output_format=output_format,
    )


# To run as an MCP server, uncomment and execute the module-level mcp instance:
if __name__ == "__main__":
    # The FastMCP instance is already created at the module level.
    # Just call its run method, specifying the transport.
    # mcp.run(transport="streamable-http")
    mcp.run(transport="streamable-http")