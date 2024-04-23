import os
import requests

from playwright.sync_api import Playwright
from playwright.sync_api import sync_playwright

from src.exceptions.download_exceptions import FileAlreadyExistException
from src.parsers.base_parser import BaseParser


class MyMailParser(BaseParser):
    BASE_DIR = os.path.abspath(f"downloads/MyMailRu")

    def get_video_link(self, playwright: Playwright):
        # TODO: проверить качество видео
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        mobile_url = f"{self.params['link'][0:8]}m.{self.params['link'][8:]}"
        page.goto(url=mobile_url)
        cc = context.cookies()
        cookies = {cookie["name"]: cookie["value"] for cookie in cc}
        link = page.get_attribute("xpath=//video", "src")
        link = "https:" + link
        title = cookies["video_key"]
        return link, title, cookies

    def video_download(self, link: str = None, title: str = None):
        if not link and not title:
            with sync_playwright() as playwright:
                link, title, cookies = self.get_video_link(playwright)

        if os.path.exists(os.path.join(os.getcwd() + f"/downloads/MyMailRu/{title}.mp4")):
            raise FileAlreadyExistException(message=f"MyMailRu/{title}.mp4")

        self.make_sure_path_exists()
        video_response = requests.get(link, cookies=cookies)
        with open(self.BASE_DIR + f"/{title}.mp4", "wb") as output:
            output.write(video_response.content)
        return f"MyMailRu/{title}.mp4"
