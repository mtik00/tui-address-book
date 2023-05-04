#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from textual.app import App, Binding, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Footer, Header, Static

from .db import Address


class AddressWidget(Static):
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
            return f"{self.address.street}\n{self.address.city}, {self.address.state} {self.address.zipcode}"

        return ""


class CombiningLayoutsExample(App):
    CSS_PATH = "css/app.css"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, name="Address Book")
        with Container(id="app-grid"):
            with VerticalScroll(id="left-pane"):
                for address in Address.select().order_by(Address.name):
                    yield AddressWidget(address)
            with VerticalScroll(id="right-pane"):
                yield AddressInfoWidget(Address.select().first())
        yield Footer()

    def new_address(self, address: Address) -> None:
        widg = self.query_one(AddressInfoWidget)
        widg.address = address


app = CombiningLayoutsExample()

if __name__ == "__main__":
    app.run()
