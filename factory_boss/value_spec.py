import logging
import re
from typing import Any, Dict, List

from faker import Faker

from factory_boss.errors import (
    ConfigurationError,
    InvalidReferenceError,
    UnresolvedReferenceError,
)
from factory_boss.instance import Instance, InstanceValue
from factory_boss.spec_parser.value_spec_registry import ValueSpecRegistry

logger = logging.getLogger(__name__)

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

    def value(self):
        raise UnresolvedReferenceError(
            f'Reference to "{self.target}" has not been resolved yet.'
        )


class ResolvedReference(Reference):
    def __init__(self, reference: Reference, resolved_target: InstanceValue):
        super().__init__(reference.target)
        self.parent = reference
        self.resolved_target: InstanceValue = resolved_target

    def value(self):
        if self.resolved_target is None:
            raise UnresolvedReferenceError(self)
        elif isinstance(self.resolved_target, Instance):
            return self.resolved_target
        else:
            return self.resolved_target.value()


class Literal(CodeToken):
    """ not a valuespec! """

    def __init__(self, value):
        self._value = value

    def value(self):
        return self._value


class ValueSpec:
    def __init__(self, type: str, name: str = None):
        self.name = name
        self.type = type
        self._references: List[Reference] = []

    def generate_value(
        self, resolved_references: Dict[Reference, ResolvedReference]
    ) -> Any:
        raise NotImplementedError(f"Not implemented for {self}")

    def references(self) -> List["Reference"]:
        return self._references

    def add_reference(self, ref: Reference):
        self._references.append(ref)

    def derived_fields(self) -> Dict[str, "ValueSpec"]:
        """Return fields derived from this field.

        An example would be a relation spec, which does not only yield the reference
        pointer, but also populates the local foreign key column."""
        return {}

    @classmethod
    def create(cls, spec: Dict[str, Any], name: str) -> "ValueSpec":
        """ Generate a value spec from a configuration dictionary. """
        raise NotImplementedError


class Constant(ValueSpec):
    def __init__(self, type, value: Any):
        super().__init__(type)
        self.value = value

    def generate_value(self, resolved_references):
        return self.value


class DynamicField(ValueSpec):
    def __init__(self, code, type, name: str = None):
        super().__init__(type=type, name=name)
        self.code = code
        self.ast: List[CodeToken] = None
        self.parse()

    @classmethod
    def create(cls, spec: Dict[str, Any], name: str) -> ValueSpec:
        if isinstance(spec, dict):
            type = spec.get("type")
            mock_info = spec.get("mock")
            if isinstance(mock_info, dict):
                return cls(code=mock_info["value"], type=type)
            else:
                return cls(code=mock_info, type=type)
        else:
            return cls(code=spec, type=None)

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
            ast = [Literal(self.code)]
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

    def __repr__(self):
        return f"{self.__class__.__name__}(code={self.code}, type={self.type}, name={self.name})"


class FakerField(ValueSpec):
    def __init__(
        self, type: str, faker_func: str, faker_kwargs: Dict = {}, name: str = None
    ):
        super().__init__(type, name=name)
        self.faker_func = faker_func
        self.faker_kwargs = faker_kwargs

    @classmethod
    def create(cls, spec: Dict, name: str):
        fakespec = spec["mock"]["faker"]
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
        return cls(spec.get("type"), faker_func, faker_kwargs)

    def generate_value(self, resolved_references):
        f = getattr(fake, self.faker_func)
        kwargs = self.faker_kwargs
        value = f(**kwargs)
        return value

    def __repr__(self):
        return f"FakerField({self.__class__.__name__}('{self.type}', '{self.faker_func}', {self.faker_kwargs})"


class RelationSpec(ValueSpec):
    """Specifies a relation between entities.

    Parameters
    ----------
    name : str
        the name of the relation field, e.g., "parent"
    relation_type : str
        one of `ONE_TO_MANY`, `MANY_TO_ONE` or `ONE_TO_ONE`
    local_field : str
        name of the key on the local side, e.g., "parent_id"
    target_entity : str
        name of the remote entity, e.g., "Person"
    target_key : str
        name of the remote key, e.g., "person_id"
    remote_name : str
        name of the remote field, e.g., "children"
    relation_strategy : str
        specifies how to choose a value during mocking.
        * "pick_random": choose a random instance of the remote entity;
        * "create": create a new instance of the remote entity;
        * "none": do not populate this relation (the remote side should take care
          of this)
    relation_overrides : Dict[str, ValueSpec]
        when `relation_strategy` is "create", this dictionary specifies overrides
        for fields of the remote instance.
    """

    ONE_TO_MANY = "1tm"
    MANY_TO_ONE = "mt1"
    ONE_TO_ONE = "1t1"

    def __init__(
        self,
        name: str,
        relation_type: str,
        local_field: str,
        target_entity: str,
        target_key: str,
        remote_name: str,
        relation_strategy: str,
        relation_overrides: Dict[str, ValueSpec],
    ):
        super().__init__(name=name, type="relation")
        self.target_entity = target_entity
        self.local_field = local_field
        self.relation_type = relation_type
        self.target_key = target_key
        self.remote_name = remote_name
        self.relation_strategy = relation_strategy
        self.relation_overrides: Dict[str, ValueSpec] = relation_overrides

    @classmethod
    def create(cls, spec: Dict, name: str = None):
        relation_type = spec["relation_type"]
        mock_info = spec.get("mock", {})
        target_entity, target_key = spec["to"].split(".")
        remote_name = spec.get("remote_name", None)
        local_field = spec["local_field"]
        relation_strategy = mock_info.get("relation_strategy", "pick_random")
        relation_overrides_dict = mock_info.get("relation_overrides", {})
        relation_overrides = {}
        for k, v in relation_overrides_dict.items():
            v = {"mock": v}
            spec_cls = ValueSpecRegistry.value_spec_cls_from_dict(v)
            specs_from_dict = spec_cls.create(v, k)
            extra = specs_from_dict.derived_fields()
            relation_overrides[k] = specs_from_dict
            relation_overrides.update(extra)

        return cls(
            name=name,
            relation_type=relation_type,
            target_entity=target_entity,
            target_key=target_key,
            remote_name=remote_name,
            local_field=local_field,
            relation_strategy=relation_strategy,
            relation_overrides=relation_overrides,
        )

    def default_value(self):
        if self.relation_type == self.ONE_TO_MANY:
            return []
        else:
            return None

    def make_remote_spec(self, local_entity: str):
        if self.relation_strategy == "none":
            raise ConfigurationError("Cannot make remote spec if strategy is 'none'.")
        if self.remote_name is None:
            return None

        if self.relation_type == self.ONE_TO_ONE:
            if self.target_entity != local_entity:
                return RelationSpec(
                    name=self.remote_name,
                    relation_type=self.ONE_TO_ONE,
                    local_field=self.target_key,
                    target_entity=local_entity,
                    target_key=self.local_field,
                    remote_name=self.name,
                    relation_strategy="none",
                    relation_overrides=None,
                )
            else:
                # it's a one-to-one relation to self,
                # so the relation already exists by definition
                return None
        elif self.relation_type == self.ONE_TO_MANY:
            return RelationSpec(
                name=self.remote_name,
                relation_type=self.MANY_TO_ONE,
                local_field=self.target_key,
                target_entity=local_entity,
                target_key=self.local_field,
                remote_name=self.name,
                relation_strategy="none",
                relation_overrides=None,
            )
        elif self.relation_type == self.MANY_TO_ONE:
            return RelationSpec(
                name=self.remote_name,
                relation_type=self.ONE_TO_MANY,
                local_field=self.target_key,
                target_entity=local_entity,
                target_key=self.local_field,
                remote_name=self.name,
                relation_strategy="none",
                relation_overrides=None,
            )

    def derived_fields(self) -> Dict[str, "ValueSpec"]:
        if self.relation_type in (self.MANY_TO_ONE, self.ONE_TO_ONE):
            return {
                self.local_field: DynamicField(
                    code=f"${self.name}.{self.target_key}",
                    type=None,
                    name=self.local_field,
                )
            }
        else:
            return super().derived_fields()


class TypeFakerSpec(FakerField):
    """ Faker for different data types """

    @classmethod
    def create(cls, spec: Dict, name: str):
        type = spec["type"]
        return cls.create_faker_for_type(type, name)

    @classmethod
    def create_faker_for_type(cls, type: str, name):
        if type == "integer":
            return cls(
                type,
                "pyint",
                {"min_value": -1_000_000, "max_value": +1_000_000},
                name=name,
            )
        elif type == "string":
            return cls(type, "pystr", {"max_chars": 20}, name=name)
        elif type == "date":
            return cls(type, "date", name=name)
        else:
            # TODO better error handling
            logger.warning(f'{cls}: unknown type "{type}". Returning Constant(None)')
            return Constant(type, None)
