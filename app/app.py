#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from textual.app import App, Binding, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Footer, Header, Label, ListItem, ListView, Static

from .db import Address, get_labels_for_address


class AddressWidget(Label):
    def __init__(self, address, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.address = address

    def render(self):
        return self.address.name

    def on_mouse_down(self, event):
        """Tell the app to update the info widget."""
        app.new_address(self.address)


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


class AddressBookApp(App):
    CSS_PATH = "css/app.css"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(name="My App")
        with Container(id="app-grid"):
            with VerticalScroll(id="left-pane"):
                children = [
                    ListItem(AddressWidget(address))
                    for address in Address.select().order_by(Address.name)
                ]
                yield ListView(*children)
            with VerticalScroll(id="right-pane"):
                yield AddressInfoWidget(Address.select().first())
        yield Footer()

    def new_address(self, address: Address) -> None:
        widg = self.query_one(AddressInfoWidget)
        widg.address = address


app = AddressBookApp()

if __name__ == "__main__":
    app.run()
