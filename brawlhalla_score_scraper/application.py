import time

from .constants import *
from .command_queue import CommandQueue
from .database import Database
from .scores import ScoreScraper
from .server.server import PlayerServer, PlayerServerDelegate


__all__ = [
    'BaseApplication',
    'Application',
    'ClientApplication'
]


class BaseApplication(Runnable, PlayerServerDelegate):
    pass


class Application(BaseApplication):
    def __init__(self, db: Database, queue: CommandQueue):
        self.db = db
        self.queue = queue
        self.scraper = ScoreScraper(self.db)
        self.server = PlayerServer(Application._get_local_ip())

        self.queue.connect(self)
        self.server.delegate = self

    def run(self):
        try:
            self.db.connect()
            for account in self.db.get_accounts():
                self.scraper.players.add_account(account)
            for player in self.db.get_players():
                self.scraper.players.add_player(player)

            self.server.run()
            self.queue.listen()

            self.scraper.run()
        finally:
            self.scraper.stop()
            self.server.stop()
            self.db.disconnect()

    # region Detail

    def get_accounts(self):
        return sorted(self.scraper.players.accounts)

    def check_event(self, event: str, data=None) -> int:

        if event == Events.Server.DeletePlayer:
            return any(p.name == data[0] for p in self.scraper.players)

        elif event == Events.Server.SetAccount:
            return (data[0] not in self.scraper.players.players) + 4 * (data[1] not in self.scraper.players.accounts)

        elif event == Events.Server.SetPlayer:
            return (data[0] not in self.scraper.players.players) + 2 * (not Legends.exists(data[1]))

        return False

    def on_event(self, event: str, data=None):

        if event == Events.Server.DeletePlayer:
            self.scraper.set_live_player(data[0], '')

        elif event == Events.Server.SetPlayer:
            self.scraper.set_live_player(*data)

        elif event == Events.Server.SetAccount:
            self.scraper.set_account(*data)

        elif event == Events.Command.Pause:
            self.scraper.paused = not self.scraper.paused

        elif event == Events.Command.AddPlayer:
            self.scraper.add_player(data)

        elif event == Events.Command.RemovePlayer:
            self.scraper.remove_player(self.scraper.players.named(data))

        elif event == Events.Command.AddAccount:
            self.scraper.add_account(data)

        elif event == Events.Command.RemoveAccount:
            self.scraper.remove_account(data)

    @staticmethod
    def _get_local_ip() -> str:
        import socket
        ip = '127.0.0.1'
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        finally:
            s.close()

        return ip

    # endregion


class ClientApplication(BaseApplication):

    def get_accounts(self):
        return []

    def run(self):
        try:
            while True:
                time.sleep(0.02)
        finally:
            pass
