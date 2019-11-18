from typing import Optional, Union

from .constants import Color

__all__ = [
    'Player',
    'Match',
    'IndividualMatch',
    'LivePlayer',
    'Score',
    'Nobody'
]


class Model:
    @classmethod
    def from_data(cls, *data):
        return cls(*data)


class Player(Model):
    def __init__(self, name: str, initials: str, color: Union[Color, int]):
        self.name = name
        self.initials = initials
        self.color = color if isinstance(color, Color) else Color.from_int(color)

    def __repr__(self):
        return "Nobody" if self.name == "" else "Player(%-2s)" % self.initials

    @classmethod
    def from_string(cls, data: str):

        # Check string format
        if data.count(',') != 2 or data.count('|') != 2:
            return None

        name, initials, rgb = data.split(',')

        # Check rgb format
        if rgb.count('|') != 2:
            return None

        color = Color(*tuple(map(int, rgb.split('|'))))

        return Player(name, initials, color)


class Match(Model):
    def __init__(self,
                 id_: int,
                 mode: str,
                 game_mode: str,
                 teams: bool,
                 player_count: int,
                 first_name: str,
                 second_name: Optional[str] = None,
                 third_name: Optional[str] = None,
                 fourth_name: Optional[str] = None):
        self.id = id_
        self.mode = mode
        self.game_mode = game_mode
        self.teams = teams
        self.player_count = player_count
        self.first_name = first_name
        self.second_name = second_name
        self.third_name = third_name
        self.fourth_name = fourth_name


class IndividualMatch(Model):
    def __init__(self,
                 match_id: int,
                 player_name: str,
                 legend: str,
                 team: int,
                 rank: int,
                 score: int,
                 kos: int,
                 falls: int,
                 accidents: int,
                 dmg_done: int,
                 dmg_taken: int):
        self.match_id = match_id
        self.player_name = player_name
        self.legend = legend
        self.team = team
        self.score = Score(rank, (score, kos, falls, accidents, dmg_done, dmg_taken))


class LivePlayer:
    def __init__(self, player: Player, legend: str):
        self.player = player
        self.legend = legend.upper()

    def __repr__(self):
        return "LiveNobody" if self.legend == "" else "LivePlayer(%-2s, %s)" % (self.player.initials, self.legend)


class Score:
    def __init__(self, rank: int, data: (int, int, int, int, int, int)):
        self.rank = rank
        # kos -> kills, accidents -> deaths ?
        self.score, \
            self.kos, \
            self.falls, \
            self.accidents, \
            self.dmg_done, \
            self.dmg_taken = data

    def __repr__(self):
        return "{rank: %d, kos: %d, falls: %d, accidents: %d, " \
               "dmg_done: %d, dmg_taken: %d}" % \
               (self.rank, self.kos, self.falls,
                self.accidents, self.dmg_done, self.dmg_taken)


Nobody = Player('', '', Color(0, 0, 0))
