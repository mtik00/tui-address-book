#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, BaseSettings

PYTERMGUI_CONFIG = """
config:
    InputField:
        styles:
            prompt: dim italic
            cursor: '@72'
    Label:
        styles:
            value: dim bold

    Window:
        styles:
            border: '60'
            corner: '60'

    Container:
        styles:
            border: '96'
            corner: '96'
"""


class DatabaseSettings(BaseModel):
    path: Optional[Path] = None


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()

    class Config:
        env_prefix = "address_book_"
        env_nested_delimiter = "__"


settings = Settings()