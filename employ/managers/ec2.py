import time

import boto.ec2
from boto.manage.cmdshell import sshclient_from_instance

from employ.exceptions import SSHConnectionError
from employ.managers import Manager


class EC2Manager(Manager):
    """
    Employ Manager which creates instances in EC2

    Config Parameters:
      [ec2]
      ami_image_id = ami-da0cf8b3
      num_instances = 1
      instance_name = employed
      region = us-east-1
      instance_type = t1.micro
      key_name = some_key
      security_group = default
      user_name = root
      host_key = ~/.ssh/known_hosts
      ssh_pwd = None

      ; when starting instances this manager will block until
      ; all instances have the state "running", this interval
      ; is how long the manager will wait between checking states
      wait_interval = 5
    """
    name = "ec2"

    def __init__(
            self, ami_image_id="ami-da0cf8b3", num_instances=1, instance_name="employed",
            region="us-east-1", instance_type="t1.micro", key_name=None, security_group="default",
            user_name="root", host_key="~/.ssh/known_hosts", ssh_pwd=None, wait_interval=5
    ):
        self.instances = []
        self.ami_image_id = ami_image_id
        self.num_instances = num_instances
        self.instance_name = instance_name
        self.region = region
        self.instance_type = instance_type
        self.key_name = key_name
        self.security_groups = [security_group] if security_group else []
        self.user_name = user_name
        self.host_key = host_key
        self.ssh_pwd = ssh_pwd
        self.wait_interval = wait_interval
        self._connection = None

    @classmethod
    def available_regions(cls):
        for region in boto.ec2.regions():
            yield region.name

    def connection(self):
        if not self._connection:
            self._connection = boto.ec2.connect_to_region(self.region)
        return self._connection

    def instance_ids(self):
        return [instance.id for instance in self.instances]

    def setup_instances(self):
        print "starting instances"
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
        connection.create_tags(self.instance_ids(), {"Name": self.instance_name})

        print "waiting until they are all running"
        while not all(instance.update() == "running" for instance in self.instances):
            time.sleep(self.wait_interval)

    __enter__ = setup_instances

    def cleanup_instances(self):
        connection = self.connection()
        connection.terminate_instances(instance_ids=self.instance_ids())

    def __exit__(self, type, value, traceback):
        self.cleanup_instances()

    def setup(self, script):
        print "setup script: %s" % script

    def run(self, command):
        # shell = sshclient_from_instance(
        #     self.instances[0], self.host_key, user_name=self.user_name
        # )
        # command.aggregate(shell.run(command.command()))
        print "running command: %s" % command.command()
