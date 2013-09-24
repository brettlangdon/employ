__version__ = "0.1.0"
from straight.plugin import load

from employ.commands import Command

commands = load("employ.commands", subclasses=Command)
