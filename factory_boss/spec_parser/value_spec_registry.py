from typing import TYPE_CHECKING, Any, Dict, Type, Union

if TYPE_CHECKING:
    from factory_boss.value_spec import ValueSpec


class ValueSpecRegistry:
    """ Given a configuration dictionary, return a matching ValueSpec subclass """

    @classmethod
    def value_spec_cls_from_dict(cls, spec: Union[Dict, Any]) -> Type["ValueSpec"]:
        from factory_boss.value_spec import (
            DynamicField,
            FakerField,
            RelationSpec,
            TypeFakerSpec,
        )

        if isinstance(spec, dict):
            mock_info = spec.get("mock")
            print(mock_info)
            if spec.get("type") == "relation":
                return RelationSpec
            elif mock_info is None:
                return TypeFakerSpec
            elif isinstance(mock_info, dict):
                if "faker" in mock_info:
                    return FakerField
                else:
                    return DynamicField
            else:
                return DynamicField
        else:
            return DynamicField
            # rspec = RelationSpec.create(spec)
            # specs = {
            #     name: rspec,
            #     rspec.local_field: DynamicField(
            #         f"${name}.{rspec.target_key}", type=None
            #     ),
            # }
            # return specs
        # else:
        #     return {name: cls.create_faker_for_type(spec["type"])}
        # else:
        #     print(f"invalid configuration {spec}. Ignoring for now.")
        #     return None
        #     raise ConfigurationError(f"invalid configuration {spec}")
