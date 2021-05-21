import random
from graphlib import TopologicalSorter
from typing import Dict, List

from factory_boss.errors import ConfigurationError
from factory_boss.instance import Instance, InstanceValue
from factory_boss.value_spec import DynamicField, ValueSpec


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
            ivalue = InstanceValue(
                name=fname, spec=field, owner=instance, context=override_context
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
                    elif rel.spec.relation_type == "1tm":
                        # TODO
                        raise NotImplementedError("1tm relation")
                    elif rel.spec.relation_type == "1t1":
                        # TODO
                        raise NotImplementedError("1t1 relation")
                    elif rel.spec.relation_type == "mt1":
                        print(f"making relation for {ename}.{rel.name}")
                        possible_targets = all_instances[rel.spec.target_entity]
                        strat = rel.spec.relation_strategy
                        if strat == "pick_random":
                            target = random_element(possible_targets)
                        elif strat == "create":
                            print("CREATING")
                            overrides: Dict[str, ValueSpec] = {
                                n: DynamicField(v, type=None)
                                for n, v in rel.spec.relation_overrides.items()
                            }
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

    def resolve_references(self, instances):
        def resolve(tokens, context):
            if len(tokens) == 1:
                token = tokens[0]
                if token == "SELF":
                    print(f"CONTEXT for {target} is", context)
                    return context
                else:
                    return context.instance_values[token]
            else:
                context = context.instance_values[tokens[0]]
                return resolve(tokens[1:], context.value())

        print("RESOLVING")
        for ename, einstances in instances.items():
            for instance in einstances:
                for ivalue in instance.instance_values.values():
                    for ref in ivalue.unresolved_references():
                        target = ref.target
                        tokens = target.split(".")
                        # print(f"Resolving {tokens} in {instance}")
                        resolved_target = resolve(tokens, ivalue.context)
                        resolved_ref = ref.resolve_to(resolved_target)
                        ivalue.add_resolved_reference(resolved_ref)
                        print(f"resolved {ref} to {resolved_target}")

    def make_plan(self, instances) -> List[InstanceValue]:
        # TODO resolve dependencies
        """ Return evaluation order of instance values """
        sorter = TopologicalSorter()
        for ename, einstances in instances.items():
            for instance in einstances:
                for ivalue in instance.instance_values.values():
                    # print(ivalue.name, ivalue.spec.references())
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
