#!/usr/bin/env python3
import logging
import os

import pendulum

from .settings import settings


TIMEZONE = "America/Denver"


def shorten_path(path):
    """
    This seems like a pretty bad idea, but I'm doing it anyway.
    I want to convert an absolute path to a kind of module-relative path.

    Something like:
        /usr/src/app/free_game_notifier/notifier/slack.py
    would be shortened to:
        notifier/slack.py
    """
    base, _ = os.path.split(__file__)
    return path.replace(base + os.path.sep, "")


class Formatter(logging.Formatter):
    """override logging.Formatter to use an aware datetime object"""

    def __init__(self, timezone, *args, **kwargs):
        self._timezone = timezone
        super().__init__(*args, **kwargs)

    def format(self, record):
        """shorten the absolute path"""
        record.pathname = shorten_path(record.pathname)
        return super().format(record)

    def converter(self, timestamp):
        dt = pendulum.from_timestamp(timestamp)
        return dt.in_tz(self._timezone)

    def formatTime(self, record, datefmt=None):
        dt = self.converter(record.created)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            s = dt.isoformat()
        return s


def set_root_level(level):
    logging.getLogger().setLevel(level)


def init_logger():
    fmt = Formatter(
        TIMEZONE,
        fmt="%(asctime)s {%(name)10s:%(lineno)3s} %(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S %Z",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    handler.setLevel("ERROR")

    handlers: list[logging.StreamHandler] = [handler]

    if settings.logging.filename:
        file_handler = logging.FileHandler(
            settings.logging.filename, mode=settings.logging.file_mode
        )
        file_handler.setFormatter(fmt)
        file_handler.setLevel(settings.logging.file_level)
        handlers.append(file_handler)

        root = logging.getLogger()
        if logging._nameToLevel[settings.logging.file_level] < root.level:
            for root_handler in [x for x in root.handlers if not x.level]:
                root_handler.setLevel(root.level)

            root.setLevel(settings.logging.file_level)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
