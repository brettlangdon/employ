from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)


class Command(object):
    """
    Base Command class that all command plugins must inherit from.
    """
    name = "command"

    def aggregate(self, results):
        """
        Method to join together the results of running :func:``command``

        Method which must be overridden by child class.

        :param results: list of (status, stdout, stderr) for each
            result of running :func:``command``
        :type results: list
        """
        raise NotImplementedError()

    def command(self):
        """
        Method to generate the command to run.

        Method which must be override by child class.

        :returns: str
        """
        raise NotImplementedError()

    @classmethod
    def from_config(cls, config):
        """
        Helper classmethod to create an instance of :class:``employ.commands.Command``
        from the provided config.

        :param config: the config to get the :class:``employ.commands.Command`` instance
        :type config: :class:``ConfigParser.RawConfigParser``
        ::returns: :class:``employ.commands.Command``
        """
        settings = {}
        if config.has_section(cls.name):
            settings = dict(config.items(cls.name))
        return cls(**settings)
