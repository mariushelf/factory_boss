from factory_boss.instance import InstanceValue


class ReferenceResolver:
    def resolve_references(self, instances):
        for instance in instances:
            for ivalue in instance.instance_values.values():
                self.resolve_references_of_instance_value(ivalue)

    def resolve_references_of_instance_value(self, ivalue: InstanceValue):
        for ref in ivalue.unresolved_references():
            target = ref.target
            tokens = target.split(".")
            resolved_target = self._resolve_token(tokens, ivalue.context)
            resolved_ref = ref.resolve_to(resolved_target)
            ivalue.add_resolved_reference(resolved_ref)

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
