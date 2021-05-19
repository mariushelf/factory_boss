from typing import Any, Dict, List

from faker import Faker

from factory_boss.context import Context
from factory_boss.errors import ConfigurationError
from factory_boss.instance import InstanceValue, ManyToOneRelationValue

fake = Faker()


class Reference:
    """ Reference to another ValueSpec """

    def __init__(self, target: str):
        self.target: str = target

    def __str__(self):
        return f"Reference({self.target})"

    def __repr__(self):
        return str(self)


class ValueSpec:
    def __init__(self, type: str):
        self.type = type

    def generate_value(self, context: Context) -> Any:
        return None  # TODO raise instead
        # raise NotImplementedError(f"Not implemented for {self}")

    def references(self) -> List["Reference"]:
        return []

    def spawn_value(self, name, owner):
        return InstanceValue(name=name, spec=self, owner=owner)


class Constant(ValueSpec):
    def __init__(self, type, value: Any):
        super().__init__(type)
        self.value = value

    def generate_value(self, context: Context):
        return self.value


class DynamicField(ValueSpec):
    def __init__(self, code: str, type):
        super().__init__(type=type)
        self.code = str(code)

    def references(self):
        if isinstance(self.code, str):
            tokens = self.code.split(" ")
            refs = []
            for t in tokens:
                if t.startswith("$"):
                    ref = Reference(t[1:])
                    refs.append(ref)
            return refs
        else:
            return []


class FakerField(ValueSpec):
    def __init__(self, type: str, faker_func: str, faker_kwargs: Dict = {}):
        super().__init__(type)
        self.faker_func = faker_func
        self.faker_kwargs = faker_kwargs

    @classmethod
    def create(cls, spec: Dict):
        fakespec = spec["faker"]
        faker_func = None
        faker_kwargs = {}
        if isinstance(fakespec, dict):
            for func, kwargs in fakespec.items():
                if faker_func:
                    raise ConfigurationError("only one fake function can be specified")
                faker_func = func
                faker_kwargs = kwargs
        else:
            faker_func = fakespec
        return FakerField(spec["type"], faker_func, faker_kwargs)

    def generate_value(self, context: Context):
        f = getattr(fake, self.faker_func)
        # kwargs = {k: v.generate_value(context) for k, v in self.faker_kwargs.items()}
        kwargs = self.faker_kwargs
        value = f(**kwargs)
        return value

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.type}', '{self.faker_func}', {self.faker_kwargs})"


class RelationSpec(ValueSpec):
    def __init__(
        self, relation_type, local_field, target_entity, target_key, remote_name
    ):
        super().__init__(type="relation")
        self.target_entity = target_entity
        self.local_field = local_field
        self.relation_type = relation_type
        self.target_key = target_key
        self.remote_name = remote_name

    @classmethod
    def create(cls, spec: Dict):
        relation_type = spec["relation_type"]
        target_entity, target_key = spec["to"].split(".")
        remote_name = spec.get("remote_name", None)
        local_field = spec["local_field"]
        return cls(
            relation_type=relation_type,
            target_entity=target_entity,
            target_key=target_key,
            remote_name=remote_name,
            local_field=local_field,
        )

    def spawn_value(self, name, owner):
        if self.relation_type == "mt1":
            return ManyToOneRelationValue(name=name, spec=self, owner=owner)
        else:
            raise NotImplementedError(
                f'Relation_type "{self.relation_type}" not yet implemented.'
            )
