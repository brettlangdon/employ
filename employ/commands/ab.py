from employ.commands import Command


class ABCommand(Command):
    """
    Command used to run ApacheBench (ab)

    Command Settings:
      [ab]
      target=<target>
      requests=<requests>
      concurrency=<concurrency>
      keepalive=(True|False)

    Eample:
      ; run_ab.ini
      [ab]
      target=http://127.0.0.1:8000/test.html
      requests=1000
      concurrency=100
      keepalive=False

      employ run ab run_ab.ini
    """
    name = "ab"

    def __init__(self, target, requests, concurrency=1, keepalive=True):
        self.target = target
        self.requests = requests
        self.concurrency = concurrency
        self.keepalive = keepalive

    def command(self):
        keepalive = " -k" if self.keepalive else ""
        return "ab %s -n %s -c %s%s" % (self.target, self.requests, self.concurrency, keepalive)

    def aggregate(self, results):
        pass
