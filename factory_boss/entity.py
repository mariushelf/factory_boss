from typing import TYPE_CHECKING, Dict

from faker import Faker

if TYPE_CHECKING:
    from factory_boss.value_spec import ValueSpec

fake = Faker()


class Entity:
    def __init__(self, name: str, fields: Dict[str, "ValueSpec"]):
        self.name = name
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
