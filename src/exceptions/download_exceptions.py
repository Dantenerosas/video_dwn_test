from src.exceptions.base_exception import DefaultException


class SiteNotImplementedException(DefaultException):
    default_message = "This site is not supported"
    error_code = "SiteNotImplemented"


class FileAlreadyExistException(DefaultException):
    default_message = "This file already exist"
    error_code = "FileAlreadyExist"

