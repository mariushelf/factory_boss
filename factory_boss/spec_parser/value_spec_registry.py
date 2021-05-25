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
