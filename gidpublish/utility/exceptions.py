

class GidPublishBaseError(Exception):
    pass


class UnknownFreezeValue(GidPublishBaseError):
    def __init__(self, line):
        self.line = line
        self.msg = f"Unable to determin package_type, package_name or package_version from '{line}'"
        super().__init__(self.msg)
