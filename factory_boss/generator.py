import random
from graphlib import TopologicalSorter
from typing import Dict, List

from factory_boss.errors import ConfigurationError
from factory_boss.instance import Instance, InstanceValue
from factory_boss.value_spec import RelationSpec, ValueSpec


class Generator:
    def __init__(self, spec):
        self.spec = spec

    def generate(self) -> Dict[str, List[Instance]]:
        """ Generate a dictionary from entity name to list of generated instances """
        new_instances = self.make_instances()
        all_instances = new_instances
        iter = 0
        while any(new_instances.values()):
            iter += 1
            print(f"ITERATION {iter}")
            new_instances = self.make_relations(new_instances, all_instances)
            print("NI")
            print(new_instances)
            for ename, einstances in new_instances.items():
                if ename not in all_instances:
                    all_instances[ename] = []
                print(f"Adding {len(einstances)} instances to {ename}")
                all_instances[ename] += einstances

        self.resolve_references(all_instances)
        plan = self.make_plan(all_instances)
        self.execute_plan(plan)
        dicts = self.instances_to_dict(all_instances)
        return dicts

    def execute_plan(self, plan):
        for ivalue in plan:
            ivalue.make_value()

    def instances_to_dict(self, instances: Dict[str, List[Instance]]):
        dicts = {}
        for ename, einstances in instances.items():
            edicts = []
            for instance in einstances:
                edicts.append(instance.to_dict())
            dicts[ename] = edicts
        return dicts

    def make_instances(self) -> Dict[str, List[Instance]]:
        """ Generate all `Instance`s including `InstanceValue`s """
        n = 3  # generate 3 instances of each entity  # TODO make configurable
        instances: Dict[str, List[Instance]] = {}
        for ename, ent in self.spec["entities"].items():
            instances[ename] = []
            for i in range(n):
                instance = self.make_instance_for_entity(ent, {})
                instances[ename].append(instance)
        return instances

    def make_instance_for_entity(
        self, entity, overrides: Dict[str, ValueSpec], override_context: Instance = None
    ) -> Instance:
        instance = Instance(entity)
        for fname, field in entity.fields.items():
            if fname in overrides:
                field = overrides[fname]
                context = override_context
            else:
                context = instance
            ivalue = InstanceValue(
                name=fname, spec=field, owner=instance, context=context
            )
            instance.instance_values[fname] = ivalue
        return instance

    def make_relations(self, instances, all_instances) -> Dict[str, List[Instance]]:
        new_instances: Dict[str, List[Instance]] = {}
        for ename, einstances in instances.items():
            print(ename)
            new_instances[ename] = []
            for instance in einstances:
                print("INSTANCE")
                for rel in instance.relations():
                    print(f"{rel.name}")
                    if rel.defined:
                        # relation already defined (probably via override). Skip.
                        print(f"{rel.name} already defined!")
                        continue
                    elif not isinstance(rel.spec, RelationSpec):
                        #
                        self.resolve_references_of_instance_value(rel)
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
                        print(f"making relation for {ename}.{rel.name}")
                        possible_targets = all_instances[rel.spec.target_entity]
                        strat = rel.spec.relation_strategy
                        if strat == "pick_random":
                            target = random_element(possible_targets)
                        elif strat == "create":
                            print("CREATING")
                            overrides = rel.spec.relation_overrides
                            print("OVERRIDES", rel.spec.relation_overrides)
                            target = self.make_instance_for_entity(
                                self.spec["entities"][rel.spec.target_entity],
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

    @classmethod
    def _resolve_token(cls, tokens, context):
        if len(tokens) == 1:
            token = tokens[0]
            if token == "SELF":
                return context
            else:
                return context.instance_values[token]
        else:
            token = tokens[0]
            if token == "SELF":
                pass
            else:
                context = context.instance_values[token].value()
            return cls._resolve_token(tokens[1:], context)

    def resolve_references(self, instances):

        print("RESOLVING")
        for ename, einstances in instances.items():
            for instance in einstances:
                for ivalue in instance.instance_values.values():
                    self.resolve_references_of_instance_value(ivalue)

    def resolve_references_of_instance_value(self, ivalue: InstanceValue):
        for ref in ivalue.unresolved_references():
            target = ref.target
            tokens = target.split(".")
            resolved_target = self._resolve_token(tokens, ivalue.context)
            resolved_ref = ref.resolve_to(resolved_target)
            ivalue.add_resolved_reference(resolved_ref)

    def make_plan(self, instances) -> List[InstanceValue]:
        """ Return evaluation order of instance values """
        sorter = TopologicalSorter()
        for ename, einstances in instances.items():
            for instance in einstances:
                for ivalue in instance.instance_values.values():
                    references = ivalue.resolved_references().values()
                    dependencies = [ref.resolved_target for ref in references]
                    sorter.add(ivalue, *dependencies)
        plan = sorter.static_order()
        plan = list(plan)
        return plan


def random_element(choices):
    if len(choices) == 0:
        raise ValueError("choices must not be empty")
    ix = random.randint(0, len(choices) - 1)
    return choices[ix]
