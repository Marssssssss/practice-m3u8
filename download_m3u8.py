# -*- coding:utf-8 -*-
import copy

import m3u8
import sys
import os
import shutil
import multiprocessing
import requests
import ffmpeg

MAX_RETRY = 3  # 最大重试次数
DEBUG_FILENAME = "debug.m3u8"
TEMP_DIR = ".temp"  # 分片暂存目录名字


def main():
    # 读取 url
    if len(sys.argv) <= 1:
        print("Need m3u8 url!")
        return
    m3u8_url = sys.argv[1]
    print(f"[STEP 1] Start download and parse m3u8 file: {m3u8_url}")

    # 加载 m3u8 文件内容 + 保存一份方便 debug
    playlist = m3u8.load(m3u8_url)
    playlist.dump(DEBUG_FILENAME)
    print(f"[STEP 2] Get m3u8 segments length: {len(playlist.segments)}")

    # 删除并重建 TEMP 目录
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.mkdir(TEMP_DIR)

    # 拼接所有需要拉取的 url 并下载
    segment_uris = dict()
    for segment in playlist.segments:
        segment_filename = segment.uri
        segment_uris[segment_filename] = os.path.join(playlist.base_uri, segment_filename)
    has_retry = 0
    pool = multiprocessing.Pool(processes=10)
    download_uris = set(segment_uris.items())
    while True:
        result = pool.map(download_segment, download_uris)
        download_uris = set(download_uris).difference([(filename, segment_uris[filename]) for filename in result])
        if not download_uris:
            print(f"[STEP 3] All segments has downloaded!")
            break
        if has_retry == MAX_RETRY:
            print(f"[End] Download failed! Reach max retries.")
            return
        print(f"[STEP 3] Some segments download failed, retry!!! failed_segments: {download_uris}")
        has_retry += 1

    # 拼接分片内容
    # 可能对分片做加密之类的操作，包括但不限于修改后缀、二进制伪装成 jpeg 或者 png 文件、算法加密等等
    # 这里先简单全部视作视频内容读取
    print(f"[STEP 4] Start merge segments!")
    inputs = []
    for filename in segment_uris:
        inputs.append(ffmpeg.input(os.path.join(TEMP_DIR, filename)))
    ffmpeg_obj = ffmpeg.concat(*inputs, v=1)  # v=1 表示只拼接视频，如果有音频需求，设置 a = 1
    ffmpeg_obj.output("output.mp4").run()
    print(f"[End] Success! Filename is output.mp4.")

    # 删掉 .temp 目录
    os.remove(DEBUG_FILENAME)
    shutil.rmtree(TEMP_DIR)


def download_segment(download_info):
    filename, uri = download_info
    print(f"[STEP 3] Start download segment: {filename}")
    response = requests.get(uri, stream=True)
    if response.status_code == 200:  # OK
        with open(os.path.join(TEMP_DIR, filename), "wb") as f:
            f.write(response.content)
        return filename
    return None


if __name__ == "__main__":
    main()
