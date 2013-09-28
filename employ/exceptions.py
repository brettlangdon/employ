class EmployError(Exception):
    """
    Base Employ Exception
    """


class ExecutionError(EmployError):
    """
    Error when executing a command
    """


class SSHConnectionError(EmployError):
    """
    Could not connect to EC2 Instance with SSH
    """
