from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)


class Command(object):
    name = "command"

    def run(self):
        raise NotImplementedError()

    def aggregate(self):
        raise NotImplementedError()

    def command(self):
        raise NotImplementedError()

    @classmethod
    def from_config(cls, config):
        settings = {}
        if config.has_section(cls.name):
            settings = dict(config.items(cls.name))
        return cls(**settings)
