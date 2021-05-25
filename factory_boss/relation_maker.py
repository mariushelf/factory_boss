import random
from typing import Dict, List

from factory_boss.entity import Entity
from factory_boss.errors import ConfigurationError
from factory_boss.instance import Instance
from factory_boss.reference_resolver import ReferenceResolver
from factory_boss.value_spec import RelationSpec


class RelationMaker:
    def make_relations(
        self, instances, all_instances, entities: Dict[str, Entity]
    ) -> Dict[str, List[Instance]]:
        new_instances: Dict[str, List[Instance]] = {}
        resolver = ReferenceResolver()
        for ename, einstances in instances.items():
            new_instances[ename] = []
            for instance in einstances:
                for rel in instance.relations():
                    if rel.defined:
                        # relation already defined (probably via override). Skip.
                        continue
                    elif not isinstance(rel.spec, RelationSpec):
                        #
                        resolver.resolve_references_of_instance_value(rel)
                        target = rel.make_value()
                        if not isinstance(target, Instance):
                            raise ConfigurationError(
                                f"{instance.entity.name}.{rel.name}: "
                                f"Overrides of relation fields must point to an Instance, not to an InstanceValue!"
                            )
                        expected_target_entity = instance.entity.fields[
                            rel.name
                        ].target_entity
                        if not target.entity.name == expected_target_entity:
                            raise ConfigurationError(
                                f"Overrides of relation fields must point "
                                f"to the same type of entity. "
                                f'Expected "{expected_target_entity}" '
                                f'but got "{target.entity.name}" '
                                f'for "{instance.entity.name}.{rel.name}"!'
                            )
                        instance.instance_values[rel.name].override_value(target)
                    elif rel.spec.relation_type == RelationSpec.ONE_TO_MANY:
                        # TODO
                        raise NotImplementedError("1tm relation")
                    elif rel.spec.relation_type == RelationSpec.ONE_TO_ONE:
                        # TODO
                        raise NotImplementedError("1t1 relation")
                    elif rel.spec.relation_type == RelationSpec.MANY_TO_ONE:
                        # print(f"making relation for {ename}.{rel.name}")
                        possible_targets = all_instances[rel.spec.target_entity]
                        strat = rel.spec.relation_strategy
                        if strat == "pick_random":
                            target = random_element(possible_targets)
                        elif strat == "create":
                            overrides = rel.spec.relation_overrides
                            entity = entities[rel.spec.target_entity]
                            target = entity.make_instance(
                                overrides,
                                override_context=instance,
                            )
                            new_instances[ename].append(target)
                        else:
                            raise ConfigurationError(
                                f'invalid relation_strategy "{strat}"'
                            )
                        instance.instance_values[rel.name].override_value(target)
        return new_instances


def random_element(choices):
    if len(choices) == 0:
        raise ValueError("choices must not be empty")
    ix = random.randint(0, len(choices) - 1)
    return choices[ix]
