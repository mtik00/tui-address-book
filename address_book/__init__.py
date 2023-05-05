#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .app import app
from .logger import init_logger

init_logger()


if __name__ == "__main__":
    app.run()
