#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, ListItem, ListView


class EditAddressScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def __init__(self, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(value=self.address.name, id="addr-name")
            yield Input(value=self.address.nickname, id="addr-nickname")
            yield Input(value=self.address.street, id="addr-street")
            yield Input(value=self.address.city, id="addr-city")
            yield Input(value=self.address.state, id="addr-state")
            yield Input(value=self.address.zipcode, id="addr-zipcode")
            with Horizontal():
                yield Button("Ok", variant="primary", id="ok")
                yield Button("Cancel", variant="primary", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        else:
            self.address.name = self.query_one("#addr-name", Input).value
            self.address.nickname = self.query_one("#addr-nickname", Input).value
            self.address.street = self.query_one("#addr-street", Input).value
            self.address.city = self.query_one("#addr-city", Input).value
            self.address.state = self.query_one("#addr-state", Input).value
            self.address.zipcode = self.query_one("#addr-zipcode", Input).value
            self.address.save()
            self.app.pop_screen()

            # Update the widgets we just modified
            wdg: ListView = self.app.query_one("#address-listview", ListView)

            item: ListItem | None = wdg.highlighted_child
            if item:
                item.refresh(layout=True)

            self.app.query_one("#address-info").refresh()

    def key_escape(self):
        self.app.pop_screen()
