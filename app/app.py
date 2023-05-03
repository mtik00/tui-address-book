#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytermgui as ptg

from .db import Address
from .settings import PYTERMGUI_CONFIG


def submit(*args, **kwargs):
    pass


def main():
    address = Address.select().first()

    with ptg.YamlLoader() as loader:
        loader.load(PYTERMGUI_CONFIG)

    with ptg.WindowManager() as manager:
        window = (
            ptg.Window(
                "",
                ptg.InputField(address.name, prompt="Name: "),
                ptg.InputField(address.street, prompt="Address: "),
                ptg.InputField(address.zipcode, prompt="Zip code: "),
                "",
                ptg.Container(
                    "Additional notes:",
                    ptg.InputField(
                        "A whole bunch of\nMeaningful notes\nand stuff", multiline=True
                    ),
                    box="EMPTY_VERTICAL",
                ),
                "",
                ["Submit", lambda *_: submit(manager, window)],
                width=60,
                box="DOUBLE",
            )
            .set_title("[210 bold]New contact")
            .center()
        )

        manager.add(window)


if __name__ == "__main__":
    main()
