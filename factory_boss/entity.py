from typing import TYPE_CHECKING, Dict

from factory_boss.errors import ConfigurationError
from factory_boss.instance import Instance, InstanceValue

if TYPE_CHECKING:
    from factory_boss.value_spec import ValueSpec

from factory_boss.value_spec import RelationSpec


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

    def add_field(self, name, field: "ValueSpec"):
        if name not in self.fields:
            self.fields[name] = field
        else:
            raise ConfigurationError(f"Field '{name}' already defined in {self}")

    def make_instance(
        self,
        overrides: Dict[str, "ValueSpec"],
        override_context: Instance = None,
    ) -> Instance:
        instance = Instance(self)
        for fname, field in self.fields.items():
            if fname in overrides:
                field = overrides[fname]
                context = override_context
            else:
                context = instance
            ivalue = InstanceValue(
                name=fname, spec=field, owner=instance, context=context
            )
            instance.instance_values[fname] = ivalue
        return instance

    def relations(self):
        return [f for f in self.fields.values() if isinstance(f, RelationSpec)]
