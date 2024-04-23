from dataclasses import dataclass
from enum import Enum

from fastapi import Form
from pydantic import BaseModel

'''
vext: Video Extension (mp4 > mov > webm > flv > other). If --prefer-free-formats is used, webm is preferred.
aext: Audio Extension (m4a > aac > mp3 > ogg > opus > webm > other). If --prefer-free-formats is used, the order changes to ogg > opus > webm > mp3 > m4a > aac
'''


class VideoFormatEnum(Enum):
    format_3gp = "3gp"
    format_flv = "flv"
    format_mp4 = "mp4"
    format_mov = "mov"
    format_webm = "webm"


class AudioFormatEnum(Enum):
    format_aac = "aac"
    format_m4a = "m4a"
    format_mp3 = "mp3"
    format_ogg = "ogg"
    format_opus = "opus"
    format_webm = "webm"
    format_wav = "wav"


class ResolutionEnum(Enum):
    resolution_240 = "240"
    resolution_360 = "360"
    resolution_480 = "480"
    resolution_720 = "720"
    resolution_1080 = "1080"
    resolution_2048 = "2048"
    resolution_3820 = "3840"


class MergeOutputFormatEnum(Enum):
    format_avi = "avi"
    format_flv = "flv"
    format_mkv = "mkv"
    format_mov = "mov"
    format_mp4 = "mp4"
    format_webm = "webm"


@dataclass
class SubmitIn:
    link: str = Form(...)
    video_format: VideoFormatEnum = Form(default=MergeOutputFormatEnum.format_webm)
    audio_format: AudioFormatEnum = Form(default=AudioFormatEnum.format_webm)
    resolution: ResolutionEnum = Form(default=ResolutionEnum.resolution_1080)
    merge_output_format: MergeOutputFormatEnum = Form(default=MergeOutputFormatEnum.format_mkv)


class CheckIn(BaseModel):
    link: str
