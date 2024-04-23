from __future__ import unicode_literals

import os

from yt_dlp import YoutubeDL


class VideoDownloader:
    SUPPORTING_WEBSITES = [
        "ok.ru", "vk.com", "www.youtube.com", "livejournal.com"
    ]
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BASE_DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")
    BASE_YOUTUBE_DIR = os.path.join(BASE_DOWNLOAD_DIR, "Youtube")

    def __init__(self, link: str, ydl_opts: dict = None, username: str = None, password: str = None):
        self.link = link
        self.ydl_opts = ydl_opts
        self.username = username
        self.password = password
        self.info = None

    def get_info(self):
        with YoutubeDL(self.ydl_opts if self.ydl_opts else {}) as ydl:
            self.info = ydl.extract_info(self.link, download=False)

    def download(self):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        base_download_dir = os.path.join(base, os.pardir, "downloads", self.info['extractor_key'])
        for root, dirs, files in os.walk(base_download_dir):
            for file in files:
                if file.find(self.info['id']) != -1 and file.find('.part') != -1:
                    os.remove(base_download_dir + f"/{file}")
        with YoutubeDL(self.ydl_opts if self.ydl_opts else {}) as ydl:
            ydl.download([self.link])
            return self.info
