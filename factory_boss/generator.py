import random
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
        plan = self.make_plan(instances)
        for ivalue in plan:
            ivalue.make_value()
        dicts = self.instances_to_dict(instances)
        return dicts

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
                        pass
                    elif rel.spec.relation_type == "1t1":
                        # TODO
                        pass
                    elif rel.spec.relation_type == "mt1":
                        possible_targets = instances[rel.spec.target_entity]
                        target = random_element(possible_targets)
                        instance.instance_values[rel.name].override_value(target)

    def make_plan(self, instances) -> List[InstanceValue]:
        # TODO resolve dependencies
        """ Return evaluation order of instance values """
        plan = []
        for ename, einstances in instances.items():
            for instance in einstances:
                for ivalue in instance.instance_values.values():
                    plan.append(ivalue)
        return plan


def random_element(choices):
    if len(choices) == 0:
        raise ValueError("choices must not be empty")
    ix = random.randint(0, len(choices) - 1)
    return choices[ix]
