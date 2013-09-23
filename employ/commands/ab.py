from employ.commands import Command


class ABCommand(Command):
    """
    Command used to run ApacheBench (ab)

    Command Options:
      <target> <requests> [<concurrency> <extra_args>]

    Examples:
      employ run ab http://127.0.0.1/test.html 1000
      employ run ab https://127.0.0.1:8000/test.html 1000 10
      employ run ab https://127.0.0.1:8000/test.html 1000 10 "-k -C 'cookie=1234'"
    """
    name = "ab"

    def __init__(self, target, requests, concurrency=1, extra_args=""):
        self.target = target
        self.requests = requests
        self.concurrency = concurrency
        self.extra_args = extra_args
        super(ABCommand, self).__init__()

    def command(self):
        return "ab %s -n %s -c %s %s" % (self.target, self.requests, self.concurrency, self.extra_args)

    def aggregate(self, results):
        pass
