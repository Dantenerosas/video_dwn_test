import errno
import os

from loguru import logger

from src.core.ydl import VideoDownloader
from src.exceptions.download_exceptions import FileAlreadyExistException


class BaseParser:
    BASE_ENCODING = 'utf-8'
    BASE_DIR = None

    def __init__(self, params: dict):
        self.params = params

    def video_download(self):
        ydl_opts = {
            "format": self.params["format"],
            "logger": logger,
            "merge_output_format": self.params["merge_output_format"],
            'outtmpl': self.params["outtmpl"],
            # "quiet": True
        }
        downloader = VideoDownloader(link=self.params["link"], ydl_opts=ydl_opts)
        downloader.get_info()

        if 'resolution' in downloader.info and downloader.info["resolution"]:
            resolution = downloader.info['resolution']
        else:
            resolution = "NA"
        if "Yahoo" in ydl_opts["outtmpl"]["default"]:
            path_to_video = f"Yahoo/{downloader.info['id']}_{resolution}.{downloader.info['ext']}"
        elif "ZenYandex" in ydl_opts["outtmpl"]["default"]:
            path_to_video = f"ZenYandex/{downloader.info['id']}_{resolution}.{downloader.info['ext']}"
        elif "Bing" in ydl_opts["outtmpl"]["default"]:
            path_to_video = f"Bing/{downloader.info['id']}_{resolution}.{downloader.info['ext']}"
        else:
            path_to_video = f"{downloader.info['extractor_key']}/{downloader.info['id']}_{resolution}.{downloader.info['ext']}"
        if os.path.exists(os.path.join(os.getcwd() + "/downloads/" + path_to_video)):
            raise FileAlreadyExistException(message=path_to_video)
        downloader.ydl_opts["quiet"] = False
        downloader.ydl_opts["quiet"] = False
        downloader.download()
        return path_to_video

    def make_sure_path_exists(self,):
        try:
            os.makedirs(self.BASE_DIR)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
            
    '''
    TODO: скорее всего добавить процедуру для конвертации итогого файла через ffmpeg, используя
    '''
