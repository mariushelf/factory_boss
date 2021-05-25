from graphlib import TopologicalSorter
from typing import Dict, List

from factory_boss.instance import Instance, InstanceValue
from factory_boss.reference_resolver import ReferenceResolver
from factory_boss.relation_maker import RelationMaker


class Generator:
    def __init__(self, spec: Dict):
        self.spec = spec
        self.relation_maker = RelationMaker()
        self.resolver = ReferenceResolver()

    def generate(self) -> Dict[str, List[Instance]]:
        """ Generate a dictionary from entity name to list of generated instances """
        instances = self.make_instances()
        instances = self.make_relations(instances)
        self.resolver.resolve_references(instances)
        plan = self.make_plan(instances)
        self.execute_plan(plan)
        dicts = self.instances_to_dict(instances)
        return dicts

    def make_instances(self) -> Dict[str, List[Instance]]:
        """ Generate all `Instance`s including `InstanceValue`s """
        n = 3  # generate 3 instances of each entity  # TODO make configurable
        instances: Dict[str, List[Instance]] = {}
        for ename, ent in self.spec["entities"].items():
            instances[ename] = []
            for i in range(n):
                instance = ent.make_instance(overrides={})
                instances[ename].append(instance)
        return instances

    def make_relations(self, instances):
        all_instances = instances
        while any(instances.values()):
            instances = self.relation_maker.make_relations(
                instances, all_instances, entities=self.spec["entities"]
            )
            for ename, einstances in instances.items():
                if ename not in all_instances:
                    all_instances[ename] = []
                all_instances[ename] += einstances
        return all_instances

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
