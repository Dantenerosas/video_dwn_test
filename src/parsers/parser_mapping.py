from collections import OrderedDict
import re

from src.parsers.Bing.bing_parser import BingParser
from src.parsers.Dzen.dzen_parser import DzenParser
from src.parsers.MyMail.my_mail_parser import MyMailParser
from src.parsers.Okru.ok_parser import OkParser
from src.parsers.Telegram.telegram_media_downloader.telegram_parser import TelegramParser
from src.parsers.Yahoo.yahoo_parser import YahooParser
from src.parsers.Yappy.yappy_parser import YappyParser
from src.parsers.base_parser import BaseParser


def compile_regex(regex):
    return re.compile(regex, re.IGNORECASE | re.DOTALL | re.MULTILINE)


parser_mapping = OrderedDict(
    {   
        compile_regex(r"^my.mail.ru/"): MyMailParser,
        compile_regex(r"^(?:www.)?(?:youtube.com|youtu.be)/"): BaseParser,
        compile_regex(r"^vk.com/"): BaseParser,
        compile_regex(r"^ok.ru/okvideo/topic"): OkParser,
        compile_regex(r"^ok.ru/video"): BaseParser,
        compile_regex(r"^...?likee.video/"): BaseParser,
        compile_regex(r"^dzen.ru/"): DzenParser,
        compile_regex(r"^yappy.media/"): YappyParser,
        compile_regex(r"^yandex.ru/"): BaseParser,
        compile_regex(r"^.*\.yahoo.com/"): YahooParser,
        compile_regex(r"^.*\.livejournal.com/"): BaseParser,
        compile_regex(r"^.*\.dzen.ru/"): BaseParser,
        compile_regex(r"^.*\.bing.com/"): BingParser,
        compile_regex(r"^t.me/"): TelegramParser,
    }
)


def get_parser(uri):
    for regex in parser_mapping:
        if regex.match(uri):
            return parser_mapping[regex]
