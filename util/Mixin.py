import logging
import sys
import colorlog

logging.basicConfig()


def set_logger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.removeHandler(root_logger.handlers[0])
    handler = colorlog.StreamHandler()
    handler.setLevel(logging.INFO)
    handler.setFormatter(
        colorlog.ColoredFormatter("%(log_color) s%(asctime)s %(filename)s line: %(lineno)s %(levelname)s: %(message)s",
                                  datefmt="%H:%M:%S",
                                  reset=True))
    root_logger.addHandler(handler)
    return root_logger


class BaseMixin:
    set_logger()

    def __init__(self):
        pass

    @property
    def logger(self):
        return logging.getLogger(self.__class__.__name__)
