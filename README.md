# m3u8 基本机制

将一个视频文件切分成多个分片，m8u3 文件记录分片的信息，比如分片的长度、分片之间的顺序等等。

参考：

- https://en.wikipedia.org/wiki/M3U
- https://docs.fileformat.com/audio/m3u/
- https://docs.fileformat.com/audio/m3u8/

# 环境

按顺序安装下面的应用：
1. ffmpeg 安装地址：https://www.gyan.dev/ffmpeg/builds/ ，下载压缩包，解压缩后放在一个地方，将 bin 加入环境变量即可

# 根据 m3u8 文件 url 下载视频

使用 `pip install -r download_m3u8_requirements.txt` 下载依赖，安装 **ffmpeg windows** 版本，
然后 `python download_m3u8.py <url>` 下载对应视频。

其中 \<url> 填写 m3u8 文件的 url 地址。

脚本步骤：
1. 下载 m3u8 文件
2. 解析 m3u8 文件，获取每个分段的 url
3. 下载所有分段
4. 用视频库将所有分段转格式拼接