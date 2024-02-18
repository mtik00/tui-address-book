#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Markdown

log = logging.getLogger(__name__)

HELP = """
## Help

* `q` -- Quit the application
* `ctrl+a` -- Select all addresses
* `ctrl+d` -- Select no addresses

## Address Actions
* `e` -- Edit the selected address
* `s` -- Select the address
* `l` -- Label all selected addresses

## File Actions
* `crtl+l` -- Reload address book
* `crtl+s` -- Save address book

### Press `escape` to close this window
"""


class HelpScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Markdown(HELP)

    def key_escape(self):
        self.app.pop_screen()
