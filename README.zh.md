# Caption Fetcher MCP Server

用于抓取 YouTube 和 Bilibili 视频字幕的MCP服务器。

## 功能特性

*   支持抓取指定 YouTube 视频的字幕。
*   支持抓取指定 Bilibili 视频的字幕。
*   支持 Streamable HTTP Transport。


## 运行和部署

### 远程 Docker 镜像

对于大多数用户，直接拉取并运行预构建的 Docker 镜像可能是最便捷的方式：

```bash
docker run -d -p 3521:3521 --name caption-fetcher-mcp -e SESSDATA='your_sessdata' -e BILI_JCT='your_bili_jct' jorkeyliu/caption-fetcher-mcp:latest
```
*(请将 `your_sessdata` 和 `your_bili_jct` 替换为您的实际凭据)*

### 本地开发

#### 安装和设置

1.  **克隆仓库:**
    ```bash
    git clone https://github.com/jorkeyliu/caption-fetcher-mcp.git
    cd caption-fetcher-mcp
    ```
2.  **创建 Conda 虚拟环境 (推荐):**
    如果您使用 Conda，可以创建一个指定 Python 版本的虚拟环境：
    ```bash
    conda create -n caption-fetcher-mcp python=3.13.3
    conda activate caption-fetcher-mcp
    ```
3.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Bilibili 凭据:**
    抓取 Bilibili 字幕需要配置以下环境变量作为登录凭据：

    *   `SESSDATA` (必须): 用于一般在获取对应用户信息时提供，通常是 GET 操作下提供，此类操作一般不会进行操作，仅读取信息（如获取个人简介、获取个人空间信息等）。
    *   `BILI_JCT` (必须): 用于进行操作用户数据时提供，通常是 POST 操作下提供，此类操作会修改用户数据（如发送评论、点赞三连、上传视频等）。
    *   `BUVID3` / `BUVID4` (非必须): 设备验证码。通常不需要提供，但如放映室内部分接口需要提供，同时与风控有关。

    请根据您的需求配置相应的环境变量。

#### 本地运行

在项目根目录下执行以下命令启动 MCP 服务器：

```bash
$env:SESSDATA="your_sessdata"; $env:BILI_JCT="your_bili_jct"; $env:BUVID3="your_buvid3"; python -m src.server
```
*(请将 `your_sessdata`, `your_bili_jct`, `your_buvid3` 替换为您的实际凭据)*

服务器将运行在 `0.0.0.0:3521` 并使用 `streamable-http` 传输协议。

#### Docker 本地部署

如果您想在本地构建并运行 Docker 镜像：

```bash
docker build -t caption-fetcher-mcp:latest .
docker run -d -p 3521:3521 --restart unless-stopped --name caption-fetcher-mcp -e SESSDATA='your_sessdata' -e BILI_JCT='your_bili_jct' caption-fetcher-mcp:latest
```
*(请将 `your_sessdata` 和 `your_bili_jct` 替换为您的实际凭据)*

#### MCP Inspector

您可以使用 MCP Inspector 工具进行本地开发测试。在终端中运行以下命令：

```bash
npx @modelcontextprotocol/inspector
```

## 提供的工具

本项目提供以下 MCP 工具：

### `get_youtube_captions`

*   **描述:** Fetches captions for a given YouTube video URL.
*   **参数:**
    *   `youtube_url` (string, required): YouTube 视频的 URL。
    *   `preferred_lang` (string, optional): 首选的字幕语言代码 (例如: "en", "zh-CN")。
*   **返回值:** 视频字幕内容。

### `get_bilibili_captions`

*   **描述:** Fetches captions for a given Bilibili video URL.
*   **参数:**
    *   `url` (string, required): Bilibili 视频的 URL。
    *   `preferred_lang` (string, optional): 首选的字幕语言代码 (默认为 "zh-CN")。
    *   `output_format` (string, optional): 输出格式 ("text" 或 "timestamped"，默认为 "text")。
*   **返回值:** 视频字幕内容，格式取决于 `output_format` 参数。

## 使用示例

要连接到此 MCP 服务器并使用其工具，您需要一个支持 Streamable HTTP Transport 的 MCP 客户端。请参考您使用的 MCP 客户端库的文档。

连接时，请使用以下配置：

*   **Transport Type:** Streamable HTTP
*   **URL:** `http://127.0.0.1:3521/mcp`

## 许可证

本项目使用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 致谢

本项目使用了以下优秀的开源库，在此表示感谢：

*   [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api): 用于抓取 YouTube 字幕。
*   [bilibili-api](https://github.com/Nemo2011/bilibili-api): 用于与 Bilibili API 交互。