from argparse import Namespace
from typing import Type

from injector import Module, Injector

from base_parser import BaseParser, Command


class AppModule(Module):
    def apply_args(self, args: Namespace):
        pass

    def get_command_type(self) -> Type[Command] | None:
        return None


class App:
    def __init__(self, *modules: AppModule):
        injector = Injector(modules)
        base_parser = injector.get(BaseParser)
        for module in modules:
            command_type = module.get_command_type()
            if command_type is not None:
                base_parser.add_command(injector.get(command_type))
        args = base_parser.parse()
        for module in modules:
            module.apply_args(args)
        args.func()
