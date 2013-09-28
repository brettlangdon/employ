from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

from employ.execptions import ExecutionError


class Manager(object):
    name = "manager"

    @classmethod
    def from_config(cls, config):
        settings = {}
        if config.has_section(cls.name):
            settings = dict(config.items(cls.name))
        return cls(**settings)

    def setup_instances(self):
        raise NotImplementedError()

    __enter__ = setup_instances

    def cleanup_instances(self):
        raise NotImplementedError()

    def __exit__(self, type, value, traceback):
        self.cleanup_instances()

    def setup(self, script):
        raise NotImplementedError()

    def run(self, command):
        raise NotImplementedError()

    def validate_results(self, results, command):
        """
        Helper method to validate the results of running commands.

        :param results: the (status, stdout, stderr) results from running `command`
        :type results: list
        :param command: the raw str command that was run
        :type command: str
        :raises: :class:``employ.exections.ExecutionError``
        """
        for status, stdout, stderr in results:
            if status != 0:
                raise ExecutionError(
                    "Non-Zero status code from executing command: %s" % command,
                    command, status, stdout, stderr,
                )
