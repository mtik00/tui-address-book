#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .app import app
from .logger import init_logger

init_logger()
app.run()
