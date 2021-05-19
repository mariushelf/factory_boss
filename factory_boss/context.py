from factory_boss.errors import ResolveError


class Context:
    def __init__(self, parent):
        self.state = {}
        self.parent = parent

    def __getitem__(self, item):
        if item in self.state:
            return self.state[item]
        elif self.parent:
            return self.parent[item]
        else:
            raise ResolveError(item)

    def __setitem__(self, key, value):
        self.state[key] = value
