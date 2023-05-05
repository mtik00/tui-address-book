#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import logging

from peewee import CharField, DateTimeField, ForeignKeyField, Model, SqliteDatabase

from .settings import settings

if not settings.database.path:
    raise ValueError("Must define the database path")

database = SqliteDatabase(settings.database.path, pragmas={"foreign_keys": 1})

log = logging.getLogger(__name__)


class BaseModel(Model):
    class Meta:
        database = database


class Label(BaseModel):
    name = CharField(primary_key=True)


class Address(BaseModel):
    name = CharField()
    street = CharField()
    city = CharField()
    state = CharField()
    zipcode = CharField()
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()  # type: ignore
        return super().save(*args, **kwargs)


class LabelAddress(BaseModel):
    label = ForeignKeyField(Label, backref="labels")
    address = ForeignKeyField(Address, backref="addresses")


def get_addresses_for_label(label: str) -> list[Address]:
    return (
        Address.select()
        .join(LabelAddress)
        .join(Label)
        .where(Label.name == label)
        .order_by(Address.name)
    )


def get_labels_for_address(name: str, street: str) -> list[Label]:
    return (
        Label.select()
        .join(LabelAddress)
        .join(Address)
        .where(Address.name == name, Address.street == street)
        .order_by(Label.name)
    )


def add_label_to_address(address: Address, label: Label):
    LabelAddress.get_or_create(label=label, address=address)
