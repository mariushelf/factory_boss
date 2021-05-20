import re
from typing import Any, Dict, List

from faker import Faker

from factory_boss.errors import (
    ConfigurationError,
    InvalidReferenceError,
    UnresolvedReferenceError,
)
from factory_boss.instance import InstanceValue  # , ManyToOneRelationValue

fake = Faker()


class CodeToken:
    def value(self):
        raise NotImplementedError


class Reference(CodeToken):
    """ Reference to another ValueSpec """

    def __init__(self, target: str):
        self.target: str = target

    def resolve_to(self, target: InstanceValue) -> "ResolvedReference":
        return ResolvedReference(self, target)

    def __str__(self):
        return f"Reference({self.target})"

    def __repr__(self):
        return str(self)


class ResolvedReference(Reference):
    def __init__(self, reference: Reference, resolved_target: InstanceValue):
        super().__init__(reference.target)
        self.parent = reference
        self.resolved_target: InstanceValue = resolved_target

    def value(self):
        if self.resolved_target is None:
            raise UnresolvedReferenceError(self)
        else:
            return self.resolved_target.value()


class Literal(CodeToken):
    """ not a valuespec! """

    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value


class ValueSpec:
    def __init__(self, type: str):
        self.type = type
        self._references: List[Reference] = []

    def generate_value(
        self, resolved_references: Dict[Reference, ResolvedReference]
    ) -> Any:
        return None  # TODO raise instead
        # raise NotImplementedError(f"Not implemented for {self}")

    def references(self) -> List["Reference"]:
        return self._references

    def add_reference(self, ref: Reference):
        self._references.append(ref)

    def spawn_value(self, name, owner):
        return InstanceValue(name=name, spec=self, owner=owner)


class Constant(ValueSpec):
    def __init__(self, type, value: Any):
        super().__init__(type)
        self.value = value

    def generate_value(self, resolved_references):
        return self.value


class DynamicField(ValueSpec):
    def __init__(self, code, type):
        super().__init__(type=type)
        self.code = code
        self.ast = None
        self.parse()

    def parse(self) -> List:
        ast: List[CodeToken] = []
        if isinstance(self.code, str):
            tokens = self.code.split(" ")
            for t in tokens:
                if len(ast) > 0:
                    ast.append(Literal(" "))
                if t.startswith("$"):
                    pattern = r"\$([a-zA-Z_][\w\.]*\w).*"
                    m = re.match(pattern, t)
                    if m is None:
                        raise InvalidReferenceError(t)
                    ref = Reference(m[1])
                    self.add_reference(ref)
                    ast.append(ref)
                else:
                    ast.append(Literal(t))
        else:
            return [Literal(self.code)]
        self.ast = ast
        return ast

    def generate_value(self, resolved_references) -> Any:
        resolved_ast = [
            resolved_references[v] if v in resolved_references else v for v in self.ast
        ]
        if len(resolved_ast) == 1:
            return resolved_ast[0].value()
        else:
            return "".join([str(v.value()) for v in resolved_ast])


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

    def generate_value(self, resolved_references):
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

    # def spawn_value(self, name, owner):
    #     if self.relation_type == "mt1":
    #         return ManyToOneRelationValue(name=name, spec=self, owner=owner)
    #     else:
    #         raise NotImplementedError(
    #             f'Relation_type "{self.relation_type}" not yet implemented.'
    #         )
