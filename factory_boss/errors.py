class FactoryBossError(Exception):
    pass


class UndefinedValueError(FactoryBossError):
    pass


class ConfigurationError(FactoryBossError):
    pass


class InvalidReferenceError(FactoryBossError):
    pass


class UnresolvedReferenceError(FactoryBossError):
    """ A reference has not been resolved yet """

    pass


class ResolveError(FactoryBossError):
    pass
