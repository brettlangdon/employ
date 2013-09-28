import time
from os.path import basename
from threading import Thread
from Queue import Queue

import boto.ec2
import paramiko

from employ.logger import logger
from employ.exceptions import SSHConnectionError
from employ.managers import Manager


class EC2Manager(Manager):
    """
    Employ Manager which creates instances in EC2

    Config Parameters::

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

      ; when attempting to gain an ssh connection, fail after
      ; connection_attempts attempts
      connection_attempts = 10

    """
    name = "ec2"

    def __init__(
            self, ami_image_id="ami-da0cf8b3", num_instances=1,
            instance_name="employed", region="us-east-1",
            instance_type="t1.micro", key_name=None,
            security_group="default", user_name="root",
            host_key="~/.ssh/known_hosts", ssh_pwd=None,
            wait_interval=5, connection_attempts=10
    ):
        """
        Construct for :class:`employ.managers.EC2Manager`

        :param ami_image_id: the ec2 ami image to use
        :type ami_image_id: str
        :param num_instances: the number of ec2 instances to start
        :type num_instances: int
        :param instance_name: the name to assign to each instance
        """
        self.instances = []
        self.client_connections = []
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
        self.connection_attempts = connection_attempts
        self._connection = None

    def connection(self):
        """
        Returns a boto connection.

        :returns: :class:`boto.ec2.connection.EC2Connection`
        """
        if not self._connection:
            self._connection = boto.ec2.connect_to_region(self.region)
        return self._connection

    def instance_ids(self):
        """
        Get list of client instance ids

        :returns: list
        """
        return [instance.id for instance in self.instances]

    def setup_instances(self):
        """
        Starts `self.num_instances` new EC2 instances and establish SSH connections to each
        """
        logger.info("starting %s instances", self.num_instances)
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

        logger.info("waiting until all instances are all 'running'")
        while not all(instance.update() == "running" for instance in self.instances):
            time.sleep(self.wait_interval)

        # connections usually take a bit, might as well wait
        # a little bit before making the first attempt
        time.sleep(self.wait_interval)
        logger.info("establishing ssh connections")
        for instance in self.instances:
            for _ in xrange(self.connection_attempts):
                logger.info(
                    "Attempting connection to %s@%s",
                    self.user_name, instance.ip_address
                )
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                try:
                    client.connect(
                        instance.ip_address, username=self.user_name,
                        key_filename=self.host_key
                    )
                    self.client_connections.append(client)
                    break
                except Exception:
                    pass
                time.sleep(self.wait_interval)
            else:
                raise SSHConnectionError(
                    "Could not establish ssh connection to %s@%s after %s attempts",
                    self.user_name, instance.ip_address, self.connection_attempts
                )

    def cleanup_instances(self):
        """
        Close all open SSH connections and terminate all instances.
        """
        for client in self.client_connections:
            client.close()

        connection = self.connection()
        connection.terminate_instances(instance_ids=self.instance_ids())

    def setup(self, script):
        """
        Run setup `script` on all instances.

        Upload `script` to each instance and execute.

        :param script: the filename of the script to upload and run
        :type script: str
        """
        remote_file = "/tmp/%s" % basename(script)
        workers = []
        for client in self.client_connections:
            worker = Thread(target=self._put_file, args=(client, script, remote_file))
            worker.daemon = True
            worker.start()
            workers.append(worker)
        for worker in workers:
            worker.join()

        command = "/bin/sh %s" % remote_file
        results = self._run_multi(command)
        self.validate_results(results, command)

    def run(self, command):
        """
        Run :class:`employ.commands.Command` `command` on all instances.
        """
        execute = command.command()
        results = self._run_multi(execute)
        self.validate_results(results, execute)
        command.aggregate(results)

    def _run_command(self, client, command, results):
        """
        Helper method for executing a single command on a client
        """
        transport = client.get_transport()
        channel = transport.open_session()
        logger.info("executing command %s", command)
        channel.get_pty()
        channel.exec_command(command)
        status = int(channel.recv_exit_status())
        stdout = ""
        while channel.recv_ready():
            stdout += channel.recv(1024)
        stderr = ""
        while channel.recv_stderr_ready():
            stderr += channel.recv_stderr(1024)
        results.put((status, stdout, stderr))

    def _run_multi(self, command):
        """
        Helper method for executing a command across all instances
        """
        results = Queue()
        workers = []
        for client in self.client_connections:
            worker = Thread(target=self._run_command, args=(client, command, results))
            worker.daemon = True
            worker.start()
            workers.append(worker)

        for worker in workers:
            worker.join()

        all_results = []
        while not results.empty():
            all_results.append(results.get())
        return all_results

    def _put_file(self, client, script, remote_file):
        """
        Helper method to upload a file to an instance
        """
        fp = open(script, "r")
        transport = client.get_transport()
        sftp_client = paramiko.SFTPClient.from_transport(transport)
        sftp_client.putfo(fp, remote_file)
