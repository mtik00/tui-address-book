#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from textual.app import App, Binding, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, ListItem, ListView, Static

from .db import Address, get_labels_for_address
from .logger import init_logger, set_root_level

log = logging.getLogger(__name__)


class AddressListItem(ListItem):
    selected = reactive(False)

    def __init__(self, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    def render(self):
        if self.selected:
            return f"* {self.address.name}"

        return self.address.name

    def watch_highlighted(self, value: bool):
        if value:
            self.app.new_address(self.address)  # type: ignore

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
                f"{', '.join([str(label.name) for label in labels])}"
            )

        return ""


class EditScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def __init__(self, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(value=self.address.name, id="addr-name")
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


class AddressBookApp(App):
    CSS_PATH = "css/app.css"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="e", action="edit", description="Edit"),
        Binding(key="s", action="select", description="Select Item"),
        Binding(key="ctrl+a", action="all", description="Select All"),
        Binding(key="ctrl+n", action="none", description="Select None"),
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

    def action_select(self):
        # Update the widgets we just modified
        wdg: ListView = self.app.query_one("#address-listview", ListView)

        item: AddressListItem | None = wdg.highlighted_child  # type: ignore
        if item:
            item.selected = not item.selected
            item.refresh()

    def action_all(self):
        for item in self.query(AddressListItem):
            item.selected = True
            item.refresh()

    def action_none(self):
        for item in self.query(AddressListItem):
            item.selected = False
            item.refresh()


app = AddressBookApp()

if __name__ == "__main__":
    init_logger()
    set_root_level("DEBUG")
    log = logging.getLogger(__name__)

    app.run()
