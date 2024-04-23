import os

from playwright.sync_api import Playwright
from playwright.sync_api import sync_playwright

from src.parsers.base_parser import BaseParser


class BingParser(BaseParser):
    BASE_DIR = os.path.abspath(f"downloads/Bing")

    def get_video_link(self, playwright: Playwright):
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url=self.params["link"], wait_until='domcontentloaded')
        link = page.get_attribute("xpath=//iframe", "src")
        return link

    def video_download(self, link: str = None, title: str = None):
        base_link = self.params["link"]
        with sync_playwright() as playwright:
            link = self.get_video_link(playwright)
        self.params["link"] = link
        self.params['outtmpl'] = f"downloads/Bing/%(id)s_%(resolution)s.%(ext)s"
        file_path = super().video_download()
        self.params["link"] = base_link
        return file_path
