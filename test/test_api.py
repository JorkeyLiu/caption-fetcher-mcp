# test/test_api.py

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

# 替换 'VIDEO_ID_HERE' 为你想测试的 YouTube 视频 ID
# 视频 ID 通常是 11 个字符，例如 'dQw4w9WgXcQ'
# 例如: 'dQw4w9WgXcQ' 是一个常用的测试视频 ID
video_id = 'JvTnTl83ylU'

try:
    # 获取视频的字幕列表
    ytt_api = YouTubeTranscriptApi()
    transcript_list = ytt_api.list(video_id)

    # 尝试查找英文或第一个可用的字幕
    # 你可以根据需要修改这里的语言代码列表
    try:
        transcript = transcript_list.find_transcript(['en'])
    except: # 捕获所有异常，包括 NoTranscriptFound
        if transcript_list:
            transcript = transcript_list[0] # 获取第一个可用的字幕
        else:
            raise Exception(f"视频 '{video_id}' 没有可用的字幕。")


    # 获取字幕内容
    fetched_transcript = transcript.fetch()

    # 使用 TextFormatter 格式化字幕为纯文本
    formatter = TextFormatter()
    text_formatted = formatter.format_transcript(fetched_transcript)

    print(f"成功获取视频 '{video_id}' 的字幕:")
    print(text_formatted)

except Exception as e:
    print(f"获取视频 '{video_id}' 字幕时发生错误: {e}")
    print("请确保视频 ID 正确，且该视频有可用的字幕。")
    print("如果遇到 IP 封锁问题，请参考 README 文档使用代理。")