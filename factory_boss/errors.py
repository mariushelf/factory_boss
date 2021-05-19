class FactoryBossError(Exception):
    pass


class UndefinedValueError(FactoryBossError):
    pass


class ConfigurationError(FactoryBossError):
    pass


class ResolveError(FactoryBossError):
    pass
