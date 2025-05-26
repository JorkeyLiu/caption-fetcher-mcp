[中文](README.zh.md)

# Caption Fetcher MCP Server

A MCP server for fetching subtitles from YouTube and Bilibili videos.

## Features

*   Supports fetching subtitles for a given YouTube video.
*   Supports fetching subtitles for a given Bilibili video.
*   Supports Streamable HTTP Transport.

## Running and Deployment

### Remote Docker Image

For most users, pulling and running the pre-built Docker image is the most convenient way:

```bash
docker run -d -p 3521:3521 --name caption-fetcher-mcp -e SESSDATA='your_sessdata' -e BILI_JCT='your_bili_jct' jorkeyliu/caption-fetcher-mcp:latest
```
*(Please replace `your_sessdata` and `your_bili_jct` with your actual credentials)*

### Local Development

#### Installation and Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/jorkeyliu/caption-fetcher-mcp.git
    cd caption-fetcher-mcp
    ```
2.  **Create a Conda virtual environment (recommended):**
    If you use Conda, you can create a virtual environment with a specific Python version:
    ```bash
    conda create -n caption-fetcher-mcp python=3.13.3
    conda activate caption-fetcher-mcp
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Bilibili Credentials:**
    Fetching Bilibili subtitles requires configuring the following environment variables as login credentials:

    *   `SESSDATA` (Required): Generally provided when fetching user information, typically for GET operations that do not modify user data (e.g., fetching profile, personal space info).
    *   `BILI_JCT` (Required): Provided for operations that modify user data, typically for POST operations (e.g., sending comments, liking/favoriting/sharing, uploading videos).
    *   `BUVID3` / `BUVID4` (Optional): Device verification code. Usually not required, but needed for some interfaces in the screening room and related to risk control.

    Please configure the appropriate environment variables according to your needs.

#### Run Locally

Execute the following command in the project root directory to start the MCP server:

```bash
$env:SESSDATA="your_sessdata"; $env:BILI_JCT="your_bili_jct"; $env:BUVID3="your_buvid3"; python -m src.server
```
*(Please replace `your_sessdata`, `your_bili_jct`, `your_buvid3` with your actual credentials)*

The server will run on `0.0.0.0:3521` and use the `streamable-http` transport protocol.

#### Docker Local Deployment

If you want to build and run the Docker image locally:

```bash
docker build -t caption-fetcher-mcp:latest .
docker run -d -p 3521:3521 --restart unless-stopped --name caption-fetcher-mcp -e SESSDATA='your_sessdata' -e BILI_JCT='your_bili_jct' caption-fetcher-mcp:latest
```
*(Please replace `your_sessdata` and `your_bili_jct` with your actual credentials)*

#### MCP Inspector

You can use the MCP Inspector tool for local development testing. Run the following command in your terminal:

```bash
npx @modelcontextprotocol/inspector
```

### Unit Tests

```bash
python -m unittest test.test_server
```

## Available Tools

This project provides the following MCP tools:

### `get_youtube_captions`

*   **Description:** Fetches captions for a given YouTube video URL.
*   **Parameters:**
    *   `youtube_url` (string, required): The URL of the YouTube video.
    *   `preferred_lang` (string, optional): Preferred subtitle language code (e.g., "en", "zh-CN").
*   **Return Value:** The video subtitle content.

### `get_bilibili_captions`

*   **Description:** Fetches captions for a given Bilibili video URL.
*   **Parameters:**
    *   `url` (string, required): The URL of the Bilibili video.
    *   `preferred_lang` (string, optional): Preferred subtitle language code (defaults to "zh-CN").
    *   `output_format` (string, optional): Output format ("text" or "timestamped", defaults to "text").
*   **Return Value:** The video subtitle content, formatted according to the `output_format` parameter.

## Usage Example

To connect to this MCP server and use its tools, you need an MCP client that supports Streamable HTTP Transport. Please refer to the documentation of your MCP client library.

When connecting, please use the following configuration:

*   **Transport Type:** Streamable HTTP
*   **URL:** `http://127.0.0.1:3521/mcp`

*(You can add specific code examples here based on the MCP client library you are using.)*

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

This project uses the following excellent open-source libraries, and we would like to express our gratitude:

*   [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api): Used for fetching YouTube subtitles.
*   [bilibili-api](https://github.com/Nemo2011/bilibili-api): Used for interacting with the Bilibili API.