__version__ = "0.1.0"
from straight.plugin import load

from employ.commands import Command
from employ.managers import Manager

commands = load("employ.commands", subclasses=Command)
managers = load("employ.managers", subclasses=Manager)


def available_commands():
    """
    Helper function to get all availabl commands.

    :returns: dict - {Command.name: :class:`employ.commands.Command`}
    """
    all_commands = {}
    for command_cls in commands:
        if command_cls.name == "command":
            continue
        all_commands[command_cls.name] = command_cls
    return all_commands


def available_managers():
    """
    Helper function to get all available managers.

    :returns: dict - {Manager.name: :class:`employ.managers.Manager`}
    """
    all_managers = {}
    for manager_cls in managers:
        if manager_cls.name == "manager":
            continue
        all_managers[manager_cls.name] = manager_cls
    return all_managers
