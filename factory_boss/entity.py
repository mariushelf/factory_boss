from typing import Dict

from faker import Faker

from factory_boss.value_spec import ValueSpec

fake = Faker()


class Entity:
    def __init__(self, fields: Dict[str, ValueSpec]):
        self.fields = fields

    def __str__(self):
        s = """Entity {

Fields
------
"""
        for n, field in self.fields.items():
            s += f"* {n}: {field}\n"
        s += "}"

        return s

    def __repr__(self):
        return str(self)
