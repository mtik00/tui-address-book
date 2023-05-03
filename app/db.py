#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime

from peewee import CharField, DateTimeField, ForeignKeyField, Model, SqliteDatabase

from .settings import settings

if not settings.database.path:
    raise ValueError("Must define the database path")

database = SqliteDatabase(settings.database.path)


class BaseModel(Model):
    class Meta:
        database = database


class Label(BaseModel):
    name = CharField(primary_key=True)


class Address(BaseModel):
    name = CharField()
    street = CharField()
    zipcode = CharField()
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
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
        .order_by(Address.name)
    )


def create_tables():
    with database:
        database.create_tables([Address, Label, LabelAddress])

    with database.atomic():
        for year in [2020, 2021, 2022, 2023]:
            Label.create(
                name=f"Christmas {year}",
            )

    with database.atomic():
        address = Address.create(
            name="The McFaddens",
            street="1313 Mockingbird Lane",
            zipcode="11111",
        )

        for year in [2021, 2022, 2023]:
            label = Label.select().where(Label.name == f"Christmas {year}").first()
            LabelAddress.create(label=label, address=address)

        address = Address.create(
            name="The Smiths",
            street="1313 Mockingbird Lane",
            zipcode="11111",
        )

        for year in [2022, 2023]:
            label = Label.select().where(Label.name == f"Christmas {year}").first()
            LabelAddress.create(label=label, address=address)
