from typing import Any, Dict

from faker import Faker

from factory_boss.entity import Entity
from factory_boss.value_spec import (
    Constant,
    DynamicField,
    FakerField,
    RelationSpec,
    ValueSpec,
)

fake = Faker()


class SpecParser:
    def parse(self, spec) -> Dict:
        entities = {}
        entity_specs = spec["entities"]
        for n, espec in entity_specs.items():
            entities[n] = self.parse_entitity(espec)
        return {"entities": entities}

    def parse_entitity(self, espec) -> Entity:
        fields = {}
        for fname, fspec in espec["fields"].items():
            new_fields = self.create_fields(fspec, fname)
            fields.update(new_fields)
        entity = Entity(fields)
        return entity

    @classmethod
    def create_fields(cls, spec: Dict[str, Any], name) -> Dict[str, ValueSpec]:
        if "faker" in spec:
            return {name: FakerField.create(spec)}
        elif "value" in spec:
            if "$" in spec["value"]:
                return {name: DynamicField(code=spec["value"], type=spec["type"])}
            else:
                return {name: Constant(spec["type"], spec["value"])}
        elif spec["type"] == "relation":
            rspec = RelationSpec.create(spec)
            specs = {
                name: rspec,
                rspec.local_field: DynamicField(
                    f"${name}.{rspec.target_key}", type=None
                ),
            }
            return specs
        else:
            return {name: cls.create_faker_for_type(spec["type"])}
        # else:
        #     print(f"invalid configuration {spec}. Ignoring for now.")
        #     return None
        #     raise ConfigurationError(f"invalid configuration {spec}")

    @staticmethod
    def create_faker_for_type(type: str):
        if type == "integer":
            return FakerField(
                type, "pyint", {"min_value": -1_000_000, "max_value": +1_000_000}
            )
        elif type == "string":
            return FakerField(type, "pystr", {"max_chars": 20})
        elif type == "date":
            return FakerField(type, "date")
        else:
            # return Constant(None)
            # TODO better error handling
            return Constant(type, None)
