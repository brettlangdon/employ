from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from employ.exceptions import ExecutionError


class Manager(object):
    """
    Base Manager class that all Manager plugins must inherit from.
    """
    name = "manager"

    @classmethod
    def from_config(cls, config):
        """
        Helper classmethod used to create an instance of :class:`employ.managers.Manager`
        from the provided `config`

        :param config: the config to get the settings from
        :type config: :class:`ConfigParser.RawConfigParser`
        :returns: :class:`employ.managers.Manager`
        """
        settings = {}
        if config.has_section(cls.name):
            settings = dict(config.items(cls.name))
        return cls(**settings)

    def setup_instances(self):
        """
        Method called to setup the required instances.

        All children must implement this method.

        The result of this method should be that all the required
        instances are created/connected to.
        """
        raise NotImplementedError()

    def __enter__(self):
        """
        Used to call :func:`setup_instances` when using in a context manager

        with manager:
            # instances are connected to
        """
        self.setup_instances()

    def cleanup_instances(self):
        """
        Method called to destroy/disconnect from instances.

        All children must implement this method.

        The result of this method should be that all instances are
        disconnected or destroy.
        """
        raise NotImplementedError()

    def __exit__(self, type, value, traceback):
        """
        Used to call :func:`cleanup_instances` when using in a context manager

        with manager:
            # instances are available
        # instances are destroyed
        """
        self.cleanup_instances()

    def setup(self, script):
        """
        Execute `script` on all instances.

        All children must implement this method.

        :param script: filename of a local script to run on each instance
        :type script: str
        """
        raise NotImplementedError()

    def run(self, command):
        """
        Execute `command` on all instances.

        All children must implement this method.

        This method should execute `command.commad()` on all instances
        as well as sending the results of all instances to `command.aggregate`

        The results will be in the following format::

            [(status, stdout, stderr), ...]

        :param command: the command to run on the instances
        :type command: :class:`employ.commands.Command`
        """
        raise NotImplementedError()

    def validate_results(self, results, command):
        """
        Helper method to validate the results of running commands.

        :param results: the (status, stdout, stderr) results from running `command`
        :type results: list
        :param command: the raw str command that was run
        :type command: str
        :raises: :class:`employ.exections.ExecutionError`
        """
        for status, stdout, stderr in results:
            if status != 0:
                raise ExecutionError(
                    "Non-Zero status code from executing command: %s" % command,
                    command, status, stdout, stderr,
                )
