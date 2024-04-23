import os
import requests

from bs4 import BeautifulSoup
from playwright.sync_api import Playwright
from playwright.sync_api import sync_playwright

from src.exceptions.download_exceptions import FileAlreadyExistException
from src.parsers.base_parser import BaseParser


class YappyParser(BaseParser):
    BASE_DIR = os.path.abspath(f"downloads/Yappy")
    # OLD WAY
    # def get_video_link(self):
    #     resp = requests.get(self.params["link"])
    #     resp.encoding = self.BASE_ENCODING
    #     soup = BeautifulSoup(resp.text, 'lxml')
    #
    #     link = soup.find('video').get("src")
    #     title = soup.find('video').get("id")
    #     return link, title

    def get_video_link(self, playwright: Playwright):
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(url=self.params["link"], wait_until='domcontentloaded')
        link = page.get_attribute("xpath=//video", "src")
        title = page.get_attribute("xpath=//video", "id")
        return link, title


    def video_download(self, link: str = None, title: str = None):
        with sync_playwright() as playwright:

            if not link and not title:
                link, title = self.get_video_link(playwright)

        if os.path.exists(os.path.join(os.getcwd() + f"/downloads/Yappy/{title}.mp4")):
            raise FileAlreadyExistException(message=f"Yappy/{title}.mp4")

        video_response = requests.get(link)
        self.make_sure_path_exists()
        with open(self.BASE_DIR + f"/{title}.mp4", "wb") as output:
            output.write(video_response.content)
        return f"Yappy/{title}.mp4"
