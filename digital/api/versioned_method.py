
class VersionedMethod(object):

    def __init__(self, name, start_version, end_version, func):
        """Versioning information for a single method

        @name: Name of the method
        @start_version: Minimum acceptable version
        @end_version: Maximum acceptable version
        @func: Method to call

        Minimum and maximum are inclusive
        """
        self.name = name
        self.start_version = start_version
        self.end_version = end_version
        self.func = func

    def __str__(self):
        return ("Version Method %s: min: %s, max: %s"
                % (self.name, self.start_version, self.end_version))