#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from textual.app import App, Binding, ComposeResult
from textual.containers import Container, Grid, VerticalScroll
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Header, Input, ListItem, ListView, Static

from .db import Address, get_labels_for_address


class AddressListItem(ListItem):
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
            Input(value=self.address.name),
            Button("Ok", variant="primary", id="ok"),
            Button("Cancel", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.app.pop_screen()
        else:
            print("TODO: Modify the address")
            self.address.name = self.query_one(Input).value
            self.address.save()
            self.app.pop_screen()
            # self.app.refresh(layout=True)


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
                yield ListView(*children)
            with VerticalScroll(id="right-pane"):
                yield AddressInfoWidget(Address.select().first())
        yield Footer()

    def new_address(self, address: Address) -> None:
        widg = self.query_one(AddressInfoWidget)
        widg.address = address

    def action_edit(self):
        address = self.query_one(AddressInfoWidget).address
        self.push_screen(EditScreen(address))
        # TODO: Figure out how to redraw the ListItem
        # self.query_one(AddressListItem, address.name).refresh()
        # self.compose()


app = AddressBookApp()

if __name__ == "__main__":
    app.run()
