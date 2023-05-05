#!/usr/bin/env python3
import logging
import os

import pendulum

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


def init_logger(logfile: str | None = None):
    fmt = Formatter(
        TIMEZONE,
        fmt="%(asctime)s {%(name)20s:%(lineno)3s} %(levelname)s: %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S %Z",
    )

    handler = logging.StreamHandler()
    handler.setFormatter(fmt)
    handler.setLevel("ERROR")

    handlers: list[logging.StreamHandler] = [handler]

    if logfile:
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(fmt)
        file_handler.setLevel("INFO")
        handlers.append(file_handler)

    logging.basicConfig(level=logging.DEBUG, handlers=handlers)
