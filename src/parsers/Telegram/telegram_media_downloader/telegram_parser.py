import os
from urllib.parse import urlparse

from loguru import logger
from pyrogram import Client
from ruamel.yaml import YAML

from src.exceptions.download_exceptions import FileAlreadyExistException
from src.parsers.Telegram.telegram_media_downloader.media_downloader import _check_config, app, download_all_chat, \
    worker
from src.parsers.base_parser import BaseParser


class TelegramParser(BaseParser):
    def video_download(self, client: Client = None):
        url_parse_result = urlparse(self.params["link"])
        channel, message_id = url_parse_result.path[1:].split('/') if "/c/" not in url_parse_result.path else \
            url_parse_result.path[3:].split('/')
        if os.path.exists(os.path.join(os.getcwd() + f"/downloads/Telegram/{message_id}.mp4")):
            raise FileAlreadyExistException(message=f"Telegram/{message_id}.mp4")
        with open(os.path.join(os.path.abspath(""), "src/parsers/Telegram/telegram_media_downloader/config.yaml"),
                  mode="r+", encoding="utf-8") as f:
            config = YAML().load(f.read())
            config["chat"][0]['download_filter'] = f"id == {message_id}"
            config["chat"][0]['chat_id'] = channel if "/c/" not in url_parse_result.path else int(f"-100{channel}")
            config["chat"][0]['last_read_message_id'] = int(message_id)

        with open(os.path.join(os.path.abspath(""), "src/parsers/Telegram/telegram_media_downloader/config.yaml"),
                  mode="w+", encoding="utf-8") as f:
            YAML().dump(config, f)
        if _check_config():
            app.loop.run_until_complete(download_all_chat(client))
            app.loop.run_until_complete(worker(client))
            client.stop()
            app.is_running = False
            logger.info("Stopped!")
        return f"Telegram/{message_id}.mp4"
