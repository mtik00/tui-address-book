#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from textual.app import App, Binding, ComposeResult
from textual.containers import Container, Grid, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, ListItem, ListView, Static

from .db import Address, get_labels_for_address
from .logger import init_logger, set_root_level


log = logging.getLogger(__name__)


class AddressListItem(ListItem):
    # address = reactive(Address.select().first())

    def __init__(self, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    def render(self):
        return self.address.name

    def watch_highlighted(self, value: bool):
        if value:
            self.app.new_address(self.address)

        super().watch_highlighted(value)


class AddressInfoWidget(Static):
    # Re-draw when the address changes
    address = reactive(Address.select().first())

    def __init__(self, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    def render(self):
        if self.address:
            labels = get_labels_for_address(self.address.name, self.address.street)
            return (
                f"{self.address.street}\n{self.address.city},"
                f"{self.address.state} {self.address.zipcode}\n\n"
                f"{', '.join([label.name for label in labels])}"
            )

        return ""


class EditScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def __init__(self, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    def compose(self) -> ComposeResult:
        yield Grid(
            Input(value=self.address.name, id="name"),
            Button("Ok", variant="primary", id="ok"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        else:
            self.address.name = self.query_one("#name").value
            self.address.save()
            self.app.pop_screen()

            # Update the widget we just modified
            wdg: AddressListItem = self.app.query_one(
                "#address-listview"
            ).highlighted_child
            wdg.address = self.address
            wdg.refresh(layout=True)


class AddressBookApp(App):
    CSS_PATH = "css/app.css"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="e", action="edit", description="Edit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(name="My App")
        with Container(id="app-grid"):
            with VerticalScroll(id="left-pane"):
                children = [
                    AddressListItem(address)
                    for address in Address.select().order_by(Address.name)
                ]
                yield ListView(*children, id="address-listview")
            with VerticalScroll(id="right-pane"):
                yield AddressInfoWidget(Address.select().first(), id="address-info")
        yield Footer()

    def new_address(self, address: Address) -> None:
        widg = self.query_one(AddressInfoWidget)
        widg.address = address
        log.info("%s: new address set", self.__class__)

    def action_edit(self):
        address = self.query_one(AddressInfoWidget).address
        self.push_screen(EditScreen(address))


app = AddressBookApp()

if __name__ == "__main__":
    init_logger("out.log")
    set_root_level("DEBUG")
    log = logging.getLogger(__name__)

    app.run()
