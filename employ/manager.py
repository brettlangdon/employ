import boto.ec2
import boto.manage

from employ import commands


class Manager(object):
    def __init__(
            self, ami_image_id="ami-da0cf8b3", num_instances=1, instance_name="deployed",
            region="us-east-1", instance_type="t1.micro", key_name=None, security_group=None
    ):
        self.instances = []
        self.ami_image_id = ami_image_id
        self.num_instances = num_instances
        self.instance_name = instance_name
        self.region = region
        self.instance_type = instance_type
        self.key_name = key_name
        self.security_groups = [security_group] if security_group else []
        self._connection = None

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

    def connection(self):
        if not self._connection:
            logger.info("Connecting to EC2")
            self._connection = boto.ec2.connect_to_region(self.region)
        return self._connection

    def setup_instances(self):
        connection = self.connection()
        reservation = connection.run_instances(
            image_id=self.ami_image_id,
            min_count=self.num_instances,
            max_count=self.num_instances,
            instance_type=self.instance_type,
            key_name=self.key_name,
            security_groups=self.security_groups,
        )
        self.instances = reservation.instances

    __enter__ = setup_instances

    def cleanup_instances(self):
        instance_ids = [instance.id for instance in self.instances]
        connection = self.connection()
        connection.terminate_instances(instance_ids=instance_ids)

    def __exit__(self, type, value, traceback):
        self.cleanup_instances()

    def setup(self, script):
        print "executing setup script: %s" % script

    def run(self, command):
        print "running command '%s'" % command.command()
