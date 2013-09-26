from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)


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
