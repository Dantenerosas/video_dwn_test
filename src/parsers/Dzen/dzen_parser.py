import json
import os
import re

from playwright.sync_api import Playwright
from playwright.sync_api import sync_playwright

from src.parsers.base_parser import BaseParser


class DzenParser(BaseParser):
    BASE_DIR = os.path.abspath(f"downloads/Dzen")

    def get_video_link(self, playwright: Playwright):
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url=self.params["link"], wait_until='domcontentloaded')
        link = page.text_content("xpath=//script[contains(text(), 'serverState')]")
        links_json_starts_with = re.findall(r'\W\WStreamInfo', link)[0]
        links_json_ends_with = re.findall(r'\W\W\W\WsocialInfo', link)[0]
        _, _, link = link.partition(links_json_starts_with)
        links, _, _ = link.partition(links_json_ends_with)
        link = json.loads(links_json_starts_with + links)["StreamInfo"][-1]["OutputStream"]
        title = json.loads(links_json_starts_with + links)["Uuid"]
        return link, title

    def video_download(self, link: str = None, title: str = None):
        with sync_playwright() as playwright:

            if not link and not title:
                link, title = self.get_video_link(playwright)

        base_link = self.params["link"]
        self.params["link"] = link
        self.params["outtmpl"] = f"downloads/ZenYandex/{title}_%(resolution)s.%(ext)s"
        file_path = super().video_download()
        self.params["link"] = base_link
        return file_path
