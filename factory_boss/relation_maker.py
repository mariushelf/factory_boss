import random
from collections import defaultdict
from typing import Dict, List, Optional

from factory_boss.entity import Entity
from factory_boss.errors import ConfigurationError
from factory_boss.instance import Instance, InstanceValue
from factory_boss.reference_resolver import ReferenceResolver
from factory_boss.value_spec import RelationSpec


class RelationMaker:
    def __init__(self, known_instances: List[Instance], entities: Dict[str, Entity]):
        self.known_instances: Dict[str, List[Instance]] = defaultdict(list)
        self.add_known_instances(known_instances)
        self.entities = entities

    def add_known_instances(self, new_instances):
        """Add new instances to this `RelationMaker`s known instances.

        This allows them, e.g., to be chosen as a target during a random pick.
        """
        for i in new_instances:
            self.known_instances[i.entity.name].append(i)

    def make_relations(self, instances) -> List[Instance]:
        all_new_instances = []
        for instance in instances:
            new_instances = self.make_relations_for_instance(instance)
            all_new_instances += new_instances
        return all_new_instances

    def make_relations_for_instance(self, instance) -> List[Instance]:
        resolver = ReferenceResolver()
        all_new_instances = []
        for rel in instance.relations():
            new_instances = self.make_one_relation(rel, resolver)
            all_new_instances += new_instances
        return all_new_instances

    def make_one_relation(self, rel: InstanceValue, resolver) -> List[Instance]:
        if not isinstance(rel.spec, RelationSpec):
            # relation not defined as RelationSpec. This happens when
            # it is set via relation_overrides.
            self.resolve_overridden_relation(rel, resolver)
            return []
        else:
            rel_type = rel.spec.relation_type
            if rel_type == RelationSpec.ONE_TO_MANY:
                # TODO
                raise NotImplementedError("1tm relation")
            elif (
                rel_type == RelationSpec.ONE_TO_ONE
                or rel_type == RelationSpec.MANY_TO_ONE
            ):
                new_instance = self.make_one_to_many_relation(rel)
                if new_instance:
                    return [new_instance]
                else:
                    return []
            else:
                raise ConfigurationError(
                    f"Unknown relation_type. Expected one of "
                    f"'{RelationSpec.ONE_TO_ONE}', '{RelationSpec.MANY_TO_ONE}' "
                    f"or '{RelationSpec.ONE_TO_MANY}', but got '{rel_type}'."
                )

    def make_one_to_many_relation(self, rel) -> Optional[Instance]:
        strat = rel.spec.relation_strategy
        if strat == "pick_random":
            possible_targets = self.known_instances[rel.spec.target_entity]
            target = self.random_element(possible_targets)
            rel.override_value(target)
            return None
        elif strat == "create":
            overrides = rel.spec.relation_overrides
            entity = self.entities[rel.spec.target_entity]
            target = entity.make_instance(
                overrides,
                override_context=rel.owner,
            )
            rel.override_value(target)
            return target
        else:
            raise ConfigurationError(
                f"Invalid relation_strategy. "
                f"Expected one of 'pick_random', 'create', "
                f"but got '{strat}' instead."
            )

    def resolve_overridden_relation(
        self, rel: InstanceValue, resolver: ReferenceResolver
    ) -> None:
        """Resolve relation that is specified by a value that is not a `RelationValue`.

        This often happens for overridden relations.

        This function makes a value for the `InstanceValue` and performs some sanity
        checks.
        """
        # Let's extract its value...
        resolver.resolve_references_of_instance_value(rel)
        target = rel.make_value()
        entity = rel.owner.entity
        # ...and check that the value is an instance:
        if not isinstance(target, Instance):
            raise ConfigurationError(
                f"{rel.owner.entity.name}.{rel.name}: "
                f"Overrides of relation fields must point to an Instance, "
                f"not to an InstanceValue!"
            )

        expected_target_entity = entity.fields[rel.name].target_entity
        if not target.entity.name == expected_target_entity:
            raise ConfigurationError(
                f"Overrides of relation fields must point to the same type of entity. "
                f'Expected "{expected_target_entity}" but got "{target.entity.name}" '
                f'for "{entity.name}.{rel.name}"'
            )

    @staticmethod
    def random_element(choices):
        if len(choices) == 0:
            raise ValueError("choices must not be empty")
        ix = random.randint(0, len(choices) - 1)
        return choices[ix]
