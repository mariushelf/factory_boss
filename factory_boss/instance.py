import typing
from pprint import pformat
from typing import Dict

from factory_boss.errors import UndefinedValueError

if typing.TYPE_CHECKING:
    from factory_boss.value_spec import Reference, ResolvedReference, ValueSpec


class Instance:
    def __init__(self, entity):
        self.entity = entity
        self.instance_values: Dict[str, InstanceValue] = {}
        self._dict = None

    def ivalue(self, name):
        return self.instance_values[name]

    def value(self, name):
        return self.instance_values[name].make_value()

    def relations(self):
        return [
            iv for iv in self.instance_values.values() if iv.spec.type == "relation"
        ]

    def to_dict(self):
        if self._dict is None:
            self._dict = {}
            for name, ivalue in self.instance_values.items():
                value = ivalue.make_value()
                if isinstance(value, Instance):
                    value = value.to_dict()
                self._dict[name] = value
        return self._dict

    def __repr__(self):
        return f"Instance({pformat(self.instance_values)})"


class InstanceValue:
    def __init__(self, name: str, spec: "ValueSpec", owner: Instance):
        self.name = name
        self.owner = owner
        self.spec = spec
        self._value = None
        self.defined = False
        self._resolved_references: Dict[Reference, ResolvedReference] = {}

    def value(self):
        if self.defined:
            return self._value
        else:
            raise UndefinedValueError(f"value of {self.name} is not defined")

    def make_value(self):
        if not self.defined:
            self._value = self.spec.generate_value(self.resolved_references())
            self.defined = True
        return self._value

    def override_value(self, value):
        self._value = value
        self.defined = True

    def add_resolved_reference(self, reference: "ResolvedReference"):
        self._resolved_references[reference.parent] = reference

    def resolved_references(self):
        return self._resolved_references

    def __repr__(self):
        return f"InstanceValue_{id(self)}({self.name}, {self._value if self.defined else '<UNDEFINED>'})"

    # def push_value(self):
    #     """ Generate value and write it to its onwer """
    #     value = self.value()
    #     self.owner[self.name] = value


# class ManyToOneRelationValue(InstanceValue):
#     def __init__(self, name: str, spec: "RelationSpec", owner: Instance):
#         super().__init__(name, spec, owner)
#
#     # def value(self):
#     #     return self.remote_instance
#
#     def push_value(self):
#         super().push_value()
#         self.owner[self.spec.local_field] = self.remote_instance[self.spec.target_key]
#         # self.remote_instance[self.spec.remote_name] = [self.owner]
