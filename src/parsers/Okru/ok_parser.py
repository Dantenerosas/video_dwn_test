import os

import requests

from bs4 import BeautifulSoup

from src.exceptions.download_exceptions import FileAlreadyExistException
from src.parsers.base_parser import BaseParser


class OkParser(BaseParser):
    BASE_DIR = os.path.abspath(f"downloads/Odnoklassniki")

    def get_video_link(self):
        try:
            resp = requests.get(self.params["link"])
            resp.encoding = self.BASE_ENCODING
            soup = BeautifulSoup(resp.text, 'lxml')
            required_div = [div for div in soup.find_all('div', {'class': 'invisible'}) if len(div['class']) < 2][0]
            video_tags = required_div.find('span').find_all_next('span', {'itemprop': "video"})
            links = [video_tag.find('a').get("href") for video_tag in video_tags]
            return links
        except Exception as ex:
            raise

    def video_download(self):
        base_link = self.params["link"]
        links = self.get_video_link()
        file_paths = []
        for link in links:
            try:
                self.params["link"] = link
                file_path = super().video_download()
                file_paths.append(file_path)
            except FileAlreadyExistException as ex:
                file_paths.append(ex.message)
                continue
        self.params["link"] = base_link
        return file_paths

