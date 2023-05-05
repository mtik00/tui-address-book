#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate the database with random addresses.
"""
import random
import sys
from pathlib import Path

import faker

# A bit of hackory to load the app module from 1 level above this script
UP_DIR = str(Path(__file__).parent / "..")
sys.path.insert(0, UP_DIR)

from address_book.db import Address, Label, LabelAddress, database  # noqa: E402

fake = faker.Faker()

years = [2019, 2020, 2021, 2022, 2023, 2024]


def create_tables():
    with database:
        database.drop_tables([Address, Label, LabelAddress])
        database.create_tables([Address, Label, LabelAddress])

    with database.atomic():
        for year in years:
            Label.create(
                name=f"Christmas {year}",
            )

    for _ in range(100):
        with database.atomic():
            address = Address.create(
                name=fake.name(),
                street=fake.street_address(),
                city=fake.city(),
                state=fake.state_abbr(),
                zipcode=fake.postcode(),
            )

            random_years = {
                random.choice(years) for _ in range(random.randint(1, len(years)))
            }

        for year in random_years:
            label = Label.select().where(Label.name == f"Christmas {year}").first()
            LabelAddress.create(label=label, address=address)


def main():
    create_tables()


if __name__ == "__main__":
    main()
