import sqlite3
from functools import wraps

from .constants import Color
from .models import *


__all__ = [
    'Database',
]


def check_connected(f):
    @wraps(f)
    def wrapped(self, *args, **kwargs):
        if self.connection is None:
            return []
            # raise RuntimeError('Database is not connected')
        return f(self, *args, **kwargs)
    return wrapped


class Database:
    def __init__(self, path: str):
        self.path = path
        self.connection = None
        self.match_count = 0

    def connect(self):
        self.connection = sqlite3.connect(self.path)
        cursor = self.connection.cursor()
        cursor.execute(SQL.Account.CreateTable)
        cursor.execute(SQL.Player.CreateTable)
        cursor.execute(SQL.Match.CreateTable)
        cursor.execute(SQL.IndividualMatch.CreateTable)
        self.connection.commit()

        cursor.execute(SQL.Match.SelectAll)
        count = cursor.fetchall()
        self.match_count = count[0] if count else 0

    def disconnect(self):
        self.connection.close()
        self.connection = None

    @check_connected
    def get_accounts(self) -> [str]:
        cursor = self.connection.cursor()
        cursor.execute(SQL.Account.SelectAll)
        return [row[0] for row in cursor.fetchall()]

    @check_connected
    def get_players(self) -> [Player]:
        cursor = self.connection.cursor()
        cursor.execute(SQL.Player.SelectAll)
        return [Player.from_data(row[0], row[1], Color.from_int(row[2])) for row in cursor.fetchall()]

    @check_connected
    def add_account(self, account: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(SQL.Account.Insert(account))
        self.connection.commit()
        return account != ""

    @check_connected
    def remove_account(self, account: str) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(SQL.Account.Delete(account))
        self.connection.commit()
        return account != ""

    @check_connected
    def add_player(self, player: Player) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(SQL.Player.Insert(player))
        self.connection.commit()
        return player.name != ""

    @check_connected
    def remove_player(self, player: Player) -> bool:
        cursor = self.connection.cursor()
        cursor.execute(SQL.Player.Delete(player))
        self.connection.commit()
        return player.name != ""

    @check_connected
    def add_scores(self, scores: [(LivePlayer, Score)]) -> bool:
        teams = False
        mode = 'couch'
        game_mode = 'stock'
        match_id = self.match_count

        cursor = self.connection.cursor()
        cursor.execute(SQL.Match.Insert(match_id, mode, game_mode, teams, scores))

        for player, score in scores:
            cursor.execute(SQL.IndividualMatch.Insert(match_id, player.player.name, player.legend, 0, score))

        self.connection.commit()

        self.match_count += 1

        return len(scores) > 0


# region SQL

# Account -> (__name__)
# Player -> (__name__, initials, color)
# Match -> (__id__, mode='couch', gameMode='stock', teams=0|1, playerCount,
#           1st_name, 2nd_name*, 3rd_name*, 4th_name*)
# IndividualMatch -> (__Match_id, player_name__, legend, team, score, kos, falls, accidents, dmg_done, dmg_taken)

class Tables:
    Account: str = 'account'
    Player: str = 'player'
    Match: str = 'match'
    IndividualMatch: str = 'individual_match'


class SQL:

    class Account:

        CreateTable: str = \
            """ CREATE TABLE IF NOT EXISTS %s ( 
                Name varchar(64) NOT NULL,
                PRIMARY KEY ( Name ) 
            ); """ % (Tables.Account,)

        SelectAll: str = 'SELECT * from %s' % Tables.Account

        @staticmethod
        def Insert(account: str) -> str:
            return """INSERT INTO %s VALUES('%s')""" % (
                Tables.Account, account)

        @staticmethod
        def Delete(account: str):
            return """DELETE FROM %s where Name = '%s'""" % (
                Tables.Account, account)

    class Player:

        CreateTable: str = \
            """ CREATE TABLE IF NOT EXISTS %s ( 
                Name varchar(64) NOT NULL, 
                Initials char(2) NOT NULL, 
                Color int NOT NULL, 
                PRIMARY KEY ( Name ) 
            ); """ % (Tables.Player,)

        SelectAll: str = 'SELECT * FROM %s' % Tables.Player
        SelectCount: str = 'SELECT COUNT(*) FROM %s' % Tables.Player

        @staticmethod
        def Insert(player: Player) -> str:
            return """INSERT INTO %s VALUES('%s', '%s', %d)""" % (
                Tables.Player, player.name, player.initials, player.color.to_int())

        @staticmethod
        def Delete(player: Player):
            return """DELETE FROM %s where Name = '%s'""" % (
                Tables.Player, player.name)

    class Match:

        CreateTable: str = \
            """CREATE TABLE IF NOT EXISTS %s (
                ID int NOT NULL,
                Mode varchar(16) NOT NULL,
                GameMode varchar(16) NOT NULL,
                Teams boolean NOT NULL,
                PlayerCount int NOT NULL,
                FirstName varchar(64) NOT NULL,
                SecondName varchar(64) NULL,
                ThirdName varchar(64) NULL,
                FourthName varchar(64) NULL,
                PRIMARY KEY (ID),
                FOREIGN KEY (FirstName) REFERENCES %s(FirstName),
                FOREIGN KEY (SecondName) REFERENCES %s(SecondName),
                FOREIGN KEY (ThirdName) REFERENCES %s(ThirdName),
                FOREIGN KEY (FourthName) REFERENCES %s(FourthName)
            );""" % (Tables.Match, Tables.Player, Tables.Player, Tables.Player, Tables.Player)

        SelectAll: str = 'SELECT * FROM %s' % Tables.Match
        SelectCount: str = 'SELECT COUNT(*) FROM %s' % Tables.Match

        @staticmethod
        def Insert(match_id: int, mode: str, game_mode: str, teams: bool, scores: [(LivePlayer, Score)]) -> str:
            names = list(map(lambda x: "'" + x[0].player.name + "'", scores)) + ['NULL'] * (4 - len(scores))
            return """INSERT INTO %s VALUES(%d,'%s','%s',%d,%d,%s,%s,%s,%s)""" % (
                Tables.Match, match_id, mode, game_mode, teams, len(scores), names[0], names[1], names[2], names[3])

    class IndividualMatch:

        CreateTable: str = \
            """CREATE TABLE IF NOT EXISTS %s (
                MatchID int NOT NULL,
                PlayerName varchar(64) NOT NULL,
                Legend varchar(32) NOT NULL,
                Team int NOT NULL,
                Rank int NOT NULL,
                Score int NOT NULL,
                KOS int NOT NULL,
                Falls int NOT NULL,
                Accidents int NOT NULL,
                DMG_Done int NOT NULL,
                DMG_Taken int NOT NULL,
                PRIMARY KEY (MatchID, PlayerName),
                FOREIGN KEY (MatchID) REFERENCES %s(MatchID),
                FOREIGN KEY (PlayerName) REFERENCES %s(PlayerName)
            )""" % (Tables.IndividualMatch, Tables.Match, Tables.Player)

        SelectAll: str = 'SELECT * FROM %s' % Tables.IndividualMatch
        SelectCount: str = 'SELECT COUNT(*) FROM %s' % Tables.IndividualMatch

        @staticmethod
        def Insert(match_id: int, name: str, legend: str, team: int, score: Score) -> str:
            return """INSERT INTO %s VALUES(%d,'%s','%s',%d,%d,%d,%d,%d,%d,%d,%d)""" % (
                Tables.IndividualMatch, match_id, name, legend, team,
                score.rank, score.score, score.kos, score.falls,
                score.accidents, score.dmg_done, score.dmg_taken)


# endregion
