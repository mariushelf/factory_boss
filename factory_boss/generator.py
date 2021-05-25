from graphlib import TopologicalSorter
from typing import Dict, List

from factory_boss.instance import Instance, InstanceValue
from factory_boss.reference_resolver import ReferenceResolver
from factory_boss.relation_maker import RelationMaker


class Generator:
    def __init__(self, spec: Dict):
        self.spec = spec
        self.resolver = ReferenceResolver()

    def generate(self) -> Dict[str, List[Dict]]:
        """ Generate a dictionary from entity name to list of generated instances """
        instances = self.make_instances()
        instances = self.make_relations(instances)
        self.resolver.resolve_references(instances)
        plan = self.make_plan(instances)
        self.execute_plan(plan)
        dicts = self.instances_to_dict(instances)
        return dicts

    def make_instances(self) -> List[Instance]:
        """ Generate all `Instance`s including `InstanceValue`s """
        n = 3  # generate 3 instances of each entity  # TODO make configurable
        instances: List[Instance] = []
        for ename, ent in self.spec["entities"].items():
            for i in range(n):
                instance = ent.make_instance(overrides={})
                instances.append(instance)
        return instances

    def make_relations(self, instances: List[Instance]) -> List[Instance]:
        all_instances = instances
        new_instances = all_instances
        relation_maker = RelationMaker([], self.spec["entities"])
        while new_instances:
            relation_maker.add_known_instances(new_instances)
            new_instances = relation_maker.make_relations(new_instances)
            all_instances += new_instances
        return all_instances

    def make_plan(self, instances) -> List[InstanceValue]:
        """ Return evaluation order of instance values """
        sorter = TopologicalSorter()
        for instance in instances:
            for ivalue in instance.instance_values.values():
                references = ivalue.resolved_references().values()
                dependencies = [ref.resolved_target for ref in references]
                sorter.add(ivalue, *dependencies)
        plan = sorter.static_order()
        plan = list(plan)
        return plan

    def execute_plan(self, plan):
        for ivalue in plan:
            ivalue.make_value()

    def instances_to_dict(self, instances: List[Instance]) -> Dict[str, List[Dict]]:
        dicts: Dict[str, List[Dict]] = {}
        for instance in instances:
            ename = instance.entity.name
            idict = instance.to_dict()
            try:
                dicts[ename].append(idict)
            except KeyError:
                dicts[ename] = [idict]
        return dicts
