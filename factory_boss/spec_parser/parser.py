from typing import TYPE_CHECKING, Any, Dict

from factory_boss.entity import Entity
from factory_boss.spec_parser.value_spec_registry import ValueSpecRegistry

if TYPE_CHECKING:
    from factory_boss.value_spec import ValueSpec


class SpecParser:
    def parse(self, spec) -> Dict:
        entities = {}
        entity_specs = spec["entities"]
        for n, espec in entity_specs.items():
            entities[n] = self.parse_entitity(n, espec)
        return {"entities": entities}

    def parse_entitity(self, name: str, espec: Dict) -> Entity:
        fields: Dict[str, ValueSpec] = {}
        for fname, fspec in espec["fields"].items():
            new_field = self.value_spec_from_dict(fspec, fname)

            extra_fields = new_field.derived_fields()
            fields[fname] = new_field
            fields.update(extra_fields)
        entity = Entity(name, fields)
        return entity

    @classmethod
    def value_spec_from_dict(cls, spec: Dict[str, Any], name) -> "ValueSpec":
        spec_cls = ValueSpecRegistry.value_spec_cls_from_dict(spec)
        value_spec = spec_cls.create(spec, name)
        return value_spec
