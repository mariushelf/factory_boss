from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from factory_boss.value_spec import ValueSpec


class Entity:
    def __init__(self, name: str, fields: Dict[str, "ValueSpec"]):
        self.name = name
        self.fields = fields

    def __str__(self):
        s = f"""Entity('{self.name}') {{

Fields
------
"""
        for n, field in self.fields.items():
            s += f"* {n}: {field}\n"
        s += "}}"

        return s

    def __repr__(self):
        return f"Entity('{self.name}', {len(self.fields)} fields)"
