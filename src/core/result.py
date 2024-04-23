import types
from enum import Enum
from inspect import Traceback


class ResultTypeEnum(Enum):
    EXCEPTION = "Error"
    DONE = "Done"
    EXIST = "Exist"


class Result:
    def __init__(self, result_type: ResultTypeEnum, value: str | dict | list = None):
        self.result_type = result_type
        self.value = value

    def __repr__(self):
        return f'Result: {self.result_type.value}. Value: {self.value if self.value else None}'
