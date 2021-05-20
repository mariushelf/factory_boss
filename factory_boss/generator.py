import random
from graphlib import TopologicalSorter
from pprint import pprint
from typing import Dict, List

from factory_boss.instance import Instance, InstanceValue


class Generator:
    def __init__(self, spec):
        self.spec = spec

    def generate(self) -> Dict[str, List[Instance]]:
        """ Generate a dictionary from entity name to list of generated instances """
        instances = self.make_instances()
        pprint(instances)
        self.make_relations(instances)
        self.resolve_references(instances)
        plan = self.make_plan(instances)
        self.execute_plan(plan)
        dicts = self.instances_to_dict(instances)
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
                instance = Instance(ent)
                for fname, field in ent.fields.items():
                    ivalue = InstanceValue(name=fname, spec=field, owner=instance)
                    instance.instance_values[fname] = ivalue
                instances[ename].append(instance)
        return instances

    def make_relations(self, instances):
        for einstances in instances.values():
            for instance in einstances:
                for rel in instance.relations():
                    if rel.spec.relation_type == "1tm":
                        # TODO
                        raise NotImplementedError("1tm relation")
                    elif rel.spec.relation_type == "1t1":
                        # TODO
                        raise NotImplementedError("1t1 relation")
                    elif rel.spec.relation_type == "mt1":
                        possible_targets = instances[rel.spec.target_entity]
                        target = random_element(possible_targets)
                        instance.instance_values[rel.name].override_value(target)

    def resolve_references(self, instances):
        def resolve(tokens, context):
            if len(tokens) == 1:
                return context.instance_values[tokens[0]]
            else:
                context = context.instance_values[tokens[0]]
                return resolve(tokens[1:], context.value())

        print("RESOLVING")
        for ename, einstances in instances.items():
            for instance in einstances:
                for ivalue in instance.instance_values.values():
                    for ref in ivalue.spec.references():
                        target = ref.target
                        tokens = target.split(".")
                        # print(f"Resolving {tokens} in {instance}")
                        resolved_target = resolve(tokens, instance)
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
