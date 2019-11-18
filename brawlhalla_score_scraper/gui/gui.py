import sounddevice
import soundfile

from ..constants import Events, Runnable
from ..application import Application, ClientApplication
from ..command_queue import ConsoleCommandQueue
from ..database import Database
from ..delegate import Delegate

__all__ = [
    'GUI'
]


# TODO: Gui with tkinter
# TODO: GUI setup/teardown

class GUI(Runnable, Delegate):
    def __init__(self, only_client=False):
        self.db = Database('Brawlhalla_Scores.db')
        self.queue = ConsoleCommandQueue()
        self.app = Application(self.db, self.queue) if not only_client else ClientApplication()

        self.app.scraper.players.connect(self)

    def run(self):
        self.app.run()

    # region Detail

    def on_event(self, event: str, data=None):

        if event == Events.Player.NewScores:
            filename = 'brawlhalla_score_scraper/data/ding.wav'
            data, fs = soundfile.read(filename, dtype='float32')
            sounddevice.play(data[:int(len(data) / 2)], fs)

            for p, s in zip(*data):
                print(p.initials, s)

        elif event == Events.Player.UpdatedAccounts \
                or event == Events.Player.UpdatedPlayers \
                or event == Events.Player.UpdatedPlayerAccounts \
                or event == Events.Player.UpdatedLivePlayers:
            print(data)

    # endregion

# endregion
