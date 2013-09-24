import boto.ec2
import boto.manage

from employ import commands


class Manager(object):
    def __init__(
            self, ami_image_id, num_instances=1, instance_name="deployed",
            region="us-east-1", instance_type="t1.micro",
    ):
        self.instances = []
        self.ami_image_id = ami_image_id
        self.num_instances = num_instances
        self.instance_name = instance_name
        self.region = region
        self.instance_type = instance_type

    def setup_instances(self):
        print "starting %s %s instances named %s in region %s" % (
            self.num_instances, self.instance_type, self.instance_name, self.region
        )

    __enter__ = setup_instances

    def cleanup_instances(self):
        print "tearing down instances"

    def __exit__(self, type, value, traceback):
        self.cleanup_instances()

    @classmethod
    def from_config(cls, config):
        settings = {}
        if config.has_section("employ"):
            settings = dict(config.items("employ"))
        return cls(**settings)

    @classmethod
    def available_regions(cls):
        for region in boto.ec2.regions():
            yield region.name

    @classmethod
    def available_commands(cls):
        all_commands = {}
        for command_cls in commands:
            if command_cls.name == "command":
                continue
            all_commands[command_cls.name] = command_cls
        return all_commands

    def setup(self, script):
        print "executing setup script: %s" % script

    def run(self, command):
        print "running command '%s'" % command.command()
