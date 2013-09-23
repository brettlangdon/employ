import boto.ec2

from employ import commands


class Manager(object):
    def __init__(self, num_instances=1, name="deployed", region="us-east-1"):
        self.instances = []
        self.num_instances = num_instances
        self.name = name
        self.region = region

    def setup_instances(self):
        print "starting %s instances named %s in region %s" % (self.num_instances, self.name, self.region)

    __enter__ = setup_instances

    def cleanup_instances(self):
        print "tearing down instances"

    def __exit__(self, type, value, traceback):
        self.cleanup_instances()

    @classmethod
    def available_regions(cls):
        for region in boto.ec2.regions():
            yield region.name

    @classmethod
    def available_commands(cls):
        all_commands = {}
        for cls in commands.__all__:
            the_cls = getattr(commands, cls)
            if the_cls.name == "command":
                continue
            all_commands[the_cls.name] = the_cls
        return all_commands

    def run(self, command):
        print "running command '%s'" % command.command()
