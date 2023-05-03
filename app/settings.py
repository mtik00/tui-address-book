#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, BaseSettings


class DatabaseSettings(BaseModel):
    path: Optional[Path] = None


class Settings(BaseSettings):
    database: DatabaseSettings = DatabaseSettings()

    class Config:
        env_prefix = "address_book_"
        env_nested_delimiter = "__"


settings = Settings()
