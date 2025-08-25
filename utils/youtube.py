# Updated youtube.py for Web-based Music Bot Mini App

import asyncio
import os
import re
import json
import glob
import random
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch

from utils.formatters import time_to_seconds


# Pick a random .txt cookie file from cookies/ folder
def cookie_txt_file():
    folder_path = os.path.join(os.getcwd(), "cookies")
    filename = os.path.join(folder_path, "logs.csv")
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_txt = random.choice(txt_files)
    with open(filename, 'a') as file:
        file.write(f'Chosen File: {cookie_txt}\n')
    return cookie_txt


# Run shell command asynchronously
async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    out, err = await proc.communicate()
    return out.decode() if proc.returncode == 0 else err.decode()


# Check total file size of yt-dlp formats
async def check_file_size(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp", "--cookies", cookie_txt_file(), "-J", link,
        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return None
    info = json.loads(stdout.decode())
    formats = info.get('formats', [])
    return sum(fmt.get('filesize', 0) for fmt in formats)


# Core YouTubeAPI for web app integration
class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="

    async def url(self, message: Message) -> Union[str, None]:
        entities = message.entities or message.caption_entities
        if not entities:
            return None
        for entity in entities:
            if entity.type == MessageEntityType.URL:
                text = message.text or message.caption
                return text[entity.offset: entity.offset + entity.length]
            elif entity.type == MessageEntityType.TEXT_LINK:
                return entity.url
        return None

    async def details(self, link: str):
        search = VideosSearch(link, limit=1)
        result = (await search.next())["result"][0]
        title = result["title"]
        duration = result.get("duration")
        thumb = result["thumbnails"][0]["url"].split("?")[0]
        vidid = result["id"]
        duration_sec = int(time_to_seconds(duration)) if duration else 0
        return title, duration, duration_sec, thumb, vidid

    async def video_url(self, link: str):
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp", "--cookies", cookie_txt_file(), "-g",
            "-f", "best[height<=720][width<=1280]", link,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return (1, stdout.decode().split("\n")[0]) if stdout else (0, stderr.decode())

    async def download_audio(self, link: str) -> str:
        def _download():
            opts = {
                "format": "bestaudio",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "cookiefile": cookie_txt_file(),
                "quiet": True,
            }
            ydl = yt_dlp.YoutubeDL(opts)
            info = ydl.extract_info(link, download=False)
            path = f"downloads/{info['id']}.{info['ext']}"
            if not os.path.exists(path):
                ydl.download([link])
            return path
        return await asyncio.get_running_loop().run_in_executor(None, _download)

    async def download_video(self, link: str) -> str:
        def _download():
            opts = {
                "format": "best[height<=720][ext=mp4]",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "cookiefile": cookie_txt_file(),
                "quiet": True,
            }
            ydl = yt_dlp.YoutubeDL(opts)
            info = ydl.extract_info(link, download=False)
            path = f"downloads/{info['id']}.{info['ext']}"
            if not os.path.exists(path):
                ydl.download([link])
            return path
        return await asyncio.get_running_loop().run_in_executor(None, _download)