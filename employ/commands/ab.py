import re

from employ.commands import Command


class ABCommand(Command):
    """
    :class:`employ.commands.Command` used to run ApacheBench (ab)

    Command Settings::

      [ab]
      target=<target>
      requests=<requests>
      concurrency=<concurrency>
      keepalive=(True|False)

    Example::

      ; run_ab.ini
      [ab]
      target=http://127.0.0.1:8000/test.html
      requests=1000
      concurrency=100
      keepalive=False

    Running::

      employ <manager> run run_ab.ini

    """
    name = "ab"

    def __init__(self, target, requests, concurrency=1, keepalive=True):
        """
        Constructor for this command

        :param target: the http[s]://<domain>:<port>/<path> to run `ab` against
        :type target: str
        :param requests: number of requests to send
        :type requests: int
        :param concurrency: concurrency to run ab with
        :type concurrency: int
        :param keepalive: whether or not to enable keepalive
        :type keepalive: bool
        """
        self.target = target
        self.requests = requests
        self.concurrency = concurrency
        self.keepalive = keepalive

    def command(self):
        """
        Generate the proper `ab` command to execute

        :returns: str
        """
        keepalive = " -k" if self.keepalive else ""
        return "ab -n %s -c %s%s %s" % (self.requests, self.concurrency, keepalive, self.target)

    def _parse_result(self, stdout):
        """
        Internal method used to parse the results of running `ab`

        :param stdout: the stdout of the command
        :type stdout: str
        :returns: tuple - (completed, failed, req_sec, time_req)
        """
        completed = 0
        failed = 0
        req_sec = 0
        time_req = 0

        match = re.search("Complete requests:\s+([0-9]+)", stdout)
        if match and match.groups():
            completed = int(match.group(1))

        match = re.search("Failed requests:\s+([0-9]+)", stdout)
        if match and match.groups():
            failed = int(match.group(1))

        match = re.search("Requests per second:\s+([0-9\.]+)", stdout)
        if match and match.groups():
            req_sec = float(match.group(1))

        match = re.search("Time per request:\s+([0-9\.]+)", stdout)
        if match and match.groups():
            time_req = float(match.group(1))

        return (completed, failed, req_sec, time_req)

    def aggregate(self, results):
        """
        The aggregate the results of multiple executions of `ab`

        :param results: list of (status, stdout, stderr) from the
            results of running :func:`command`
        :type results: list
        """
        total_completed = 0
        total_failed = 0
        avg_req_sec = 0
        avg_time_req = 0

        for status, stdout, stderr in results:
            completed, failed, req_sec, time_req = self._parse_result(stdout)
            total_completed += completed
            total_failed += failed
            avg_req_sec += req_sec
            avg_time_req += time_req

        avg_req_sec = avg_req_sec / len(results)
        avg_time_req = avg_time_req / len(results)
        print "Results:"
        print "  Total Completed Requests: %s" % total_completed
        print "  Total Failed Requests: %s" % total_failed
        print "  Average Requests per Second: %s" % avg_req_sec
        print "  Average Time per Second: %s" % avg_time_req
