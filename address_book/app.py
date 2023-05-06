#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from textual.app import App, Binding, ComposeResult
from textual.containers import Container, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Footer, Header, ListItem, ListView, Static

from .db import Address, Label, add_label_to_address, get_labels_for_address
from .modals.edit_address import EditAddressScreen

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


class AddressBookApp(App):
    CSS_PATH = "css/app.css"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="e", action="edit", description="Edit"),
        Binding(key="s", action="select", description="Select Item"),
        Binding(key="ctrl+a", action="all", description="Select All"),
        Binding(key="ctrl+n", action="none", description="Select None"),
        Binding(key="l", action="label", description="Label selected items"),
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
        self.push_screen(EditAddressScreen(address))

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

    def action_label(self):
        label = Label.select().where(Label.name == "Christmas 2024").first()
        for item in self.query(AddressListItem):
            if item.selected:
                add_label_to_address(label=label, address=item.address)
                item.refresh()
        self.query_one("#address-info").refresh()


if __name__ == "__main__":
    app = AddressBookApp()

    log = logging.getLogger(__name__)

    app.run()
