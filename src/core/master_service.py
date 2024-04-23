import asyncio
import concurrent.futures as pool
import subprocess
import pyrogram
import traceback

from functools import partial
from urllib.parse import urlparse
from loguru import logger

from src.core.async_queue import AsyncQueue
from src.core.rabbitmq import get_messages, publish_message_with_task_done
from src.core.redis_client import RedisClient
from src.core.result import Result, ResultTypeEnum
from src.exceptions.download_exceptions import FileAlreadyExistException, SiteNotImplementedException
from src.parsers.MyMail.my_mail_parser import MyMailParser
from src.parsers.Telegram.telegram_media_downloader.media_downloader import app, _check_config
from src.parsers.Yappy.yappy_parser import YappyParser
from src.parsers.base_parser import BaseParser
from src.parsers.parser_mapping import get_parser
from src.parsers.Telegram.telegram_media_downloader.telegram_parser import TelegramParser


class MasterService:
    def __init__(self):
        self.loop = asyncio.get_event_loop()

        self.MAX_EXECUTOR_WORKERS = 8
        self.executor = pool.ProcessPoolExecutor(max_workers=self.MAX_EXECUTOR_WORKERS,
                                                 initializer=executor_initializer)
        self.queue = AsyncQueue()
        self.rabbit_consumer = get_messages
        self.currently_underway = {}  # contains currently in progress videos

    async def run(self):
        subprocess.run(
            "for pid in $(ps -ef | grep video_downloader_executor_process | awk '{print $2}'); do kill -9 $pid; done",
            shell=True, capture_output=True
        )

        tasks = [self.loop.create_task(self.create_workers()) for i in range(self.MAX_EXECUTOR_WORKERS + 1)]

        await asyncio.gather(self.rabbit_consumer(self.queue), *tasks)

    async def result_processing(self, result: Result | list, redis: RedisClient, video_params: dict):
        await redis.del_task_from_tasks_and_add_to_task_done(task=result.value, link=video_params["link"])
        await publish_message_with_task_done(task=result.value)
        self.queue.task_done()

    async def create_workers(self):
        while True:
            video_params = await self.queue.get()
            redis = RedisClient()
            await redis.del_tasks_queue()
            await redis.del_task_from_queue_and_add_to_tasks(link=video_params["link"], task=video_params)
            self.currently_underway[video_params['link']] = video_params

            download_task = self.loop.run_in_executor(self.executor, partial(
                MasterService.video_processing_executor, video_params=video_params
            ))

            result: Result = await download_task
            await self.result_processing(result, redis, video_params)

            if video_params['link'] in self.currently_underway:
                del self.currently_underway[video_params['link']]

    @staticmethod
    def video_download(video_params: dict):
        downloader: BaseParser | YappyParser | MyMailParser | TelegramParser = MasterService.get_parser(video_params)
        match downloader:
            case TelegramParser():
                if _check_config():
                    tg_client = pyrogram.Client(
                        "media_downloader",
                        api_id=app.api_id,
                        api_hash=app.api_hash,
                        proxy=app.proxy,
                        workdir=app.session_file_path,
                    )
                    app.pre_run()
                    app.is_running = True
                    tg_client.start()
                    result = downloader.video_download(client=tg_client)
                    return result
            case _:
                result = downloader.video_download()
                return result



    @staticmethod
    def get_parser(params: dict):
        try:
            url_parse_result = urlparse(params["link"])
            uri = f"{url_parse_result.netloc}{url_parse_result.path}"
            logger.info(uri)
            # # TODO: похоже нужно переделать на регулярки, т.к. добавлять каждую вариацию домена моветон, вероятно я сделаюне-
            # parser_mapping = {
            #     "my.mail.ru": MyMailParser(params),
            #     "www.youtube.com": BaseParser(params),
            #     "youtube.com": BaseParser(params),
            #     "youtu.be": BaseParser(params),
            #     "vk.com": BaseParser(params),
            #     "ok.ru": BaseParser(params) if "topic" not in params["link"] else OkParser(params),
            #     "likee.video": BaseParser(params),
            #     "dzen.ru": BaseParser(params),
            #     "yappy.media": YappyParser(params),
            #     "yandex.ru": BaseParser(params),
            # }
            return get_parser(uri)(params)
        except KeyError:
            raise SiteNotImplementedException

    @staticmethod
    def video_processing_executor(video_params: dict):
        try:
            result = MasterService.video_download(video_params=video_params)
            return Result(result_type=ResultTypeEnum.DONE, value={
                "link": video_params["link"],
                "result": result,
                "status": "done"
            }) if not isinstance(result, list)\
                else Result(result_type=ResultTypeEnum.DONE, value={
                    "link": video_params["link"],
                    "result": [result_part for result_part in result],
                    "status": "done"
                })

        except FileAlreadyExistException as ex:
            return Result(result_type=ResultTypeEnum.EXIST, value={
                "link": video_params["link"],
                "result": ex.message,
                "status": "exist"
            })
        except SiteNotImplementedException as ex:
            return Result(result_type=ResultTypeEnum.EXCEPTION, value={
                "link": video_params["link"],
                "result": ex.default_message,
                "status": "error"
            })
        except Exception as ex:
            return Result(result_type=ResultTypeEnum.EXCEPTION, value={
                "link": video_params["link"],
                "result": traceback.format_exc(),
                "status": "error"
            })
        # TODO upload to server


def executor_initializer():
    import setproctitle
    setproctitle.setproctitle(f'video_downloader_executor_process')
    return True
