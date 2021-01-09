

class GidPublishBaseError(Exception):
    pass


class UnknownFreezeValue(GidPublishBaseError):
    def __init__(self, line):
        self.line = line
        self.msg = f"Unable to determin package_type, package_name or package_version from '{line}'"
        super().__init__(self.msg)


class ExtensionAlreadyRegisteredError(GidPublishBaseError):
    def __init__(self, name, absolute_path):
        self.msg = f"extension '{name}' is already registered, saved in '{absolute_path}'"
        super().__init__(self.msg)


class ExtensionLoadError(GidPublishBaseError):
    def __init__(self, name, spec, reason, error):
        self.msg = f"unable to load extension '{name}' from '{spec.origin}'. reason: '{reason}'. error: '{str(error)}'"
        super().__init__(self.msg)


class UnsetExecutableError(GidPublishBaseError):
    def __init__(self, executable):
        self.msg = f"executable '{executable}' was not set at initialization time"
        super().__init__(self.msg)
