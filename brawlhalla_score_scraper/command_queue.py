import time
from abc import ABC, abstractmethod
from threading import Thread
from typing import Any

from .constants import Events
from .delegate import Emitter
from .models import Player


__all__ = [
    'CommandQueue',
    'ConsoleCommandQueue',
]


class CommandQueue(ABC, Emitter):

    def __init__(self):
        super().__init__()
        self.update_interval = 0.05
        self._thread = Thread(target=self._run)
        self._thread.daemon = True

    @abstractmethod
    def get_next_command_and_args(self) -> (str, [Any]):
        pass

    def listen(self):
        self._thread.start()

    def _run(self):

        # self.connect(2000)
        # self.wait_for_client()

        try:
            while True:
                time.sleep(self.update_interval)

                cmd, args = self.get_next_command_and_args()

                if cmd == 'error':
                    continue

                elif cmd == Events.Command.AddPlayer:
                    data = Player.from_string(args[0])
                    if data:
                        self.on_event(cmd, data)

                elif cmd == Events.Command.RemovePlayer \
                        or cmd == Events.Command.AddAccount \
                        or cmd == Events.Command.RemoveAccount:

                    for name in args:
                        self.on_event(cmd, name)
        finally:
            pass


class ConsoleCommandQueue(CommandQueue):

    def get_next_command_and_args(self) -> (str, [Any]):
        split = str(input('> ')).split(' ')
        if not split or len(split) < 2:
            return 'error', ''
        return split[0].lower(), split[1:]
