import time
from collections import defaultdict

from .constants import Events, Runnable
from .models import Player, LivePlayer, Score, Nobody
from .database import Database
from .delegate import Emitter, on_event
from .screen import *


__all__ = [
    'ScoreScraper',
]

waiting_for_scores = 1 << 10
waiting_for_names = 1 << 11
waiting_for_new_game = 1 << 12


# TODO: Refactor Scores data model

class ScoreScraper(Runnable):

    def __init__(self, db: Database):
        self.update_interval = 0.25
        self.db = db
        self.players = PlayerCache()
        self.state = waiting_for_scores
        self.paused = False
        self.running = True
        self.queue = []

    def add_account(self, account: str):
        if account in self.players.accounts:
            return

        self.queue.append((Events.Command.AddAccount, account))

    def remove_account(self, account: str):

        if account not in self.players.accounts:
            return

        self.queue.append((Events.Command.RemoveAccount, account))

    def add_player(self, player: Player):

        if player.name in self.players.players:
            return

        self.queue.append((Events.Command.AddPlayer, player))

    def remove_player(self, player: Player):

        if player.name not in self.players.players:
            return

        self.queue.append((Events.Command.RemovePlayer, player))

    def set_account(self, player: str, account: str):

        self.players.set_account(player, account)

    def set_live_player(self, name: str, legend: str):

        self.players.set_live_player(self.players.named(name), legend)

    def stop(self):

        self.running = False

    def run(self):

        while self.running:
            try:
                time.sleep(self.update_interval)

                self._process_queues()

                if self.paused:
                    continue

                elif self.state == waiting_for_scores:
                    if is_on_scores_screen():
                        self.players.add_scores(get_scores_from_screen())
                        self.state = waiting_for_names

                elif self.state == waiting_for_names:
                    if self.players.has_player_for_each_legend_and_score():
                        scores = self.players.get_scores()
                        if self.db.add_scores(scores):
                            on_event(self.players.delegate, Events.Player.NewScores, scores)
                        self.state = waiting_for_new_game

                elif self.state == waiting_for_new_game:
                    if is_on_character_select_screen():
                        self.state = waiting_for_scores

            except KeyboardInterrupt:
                break

    def _process_queues(self):
        for command, data in self.queue:

            if command == Events.Command.AddAccount:
                if self.db.add_account(data):
                    self.players.add_account(data)

            elif command == Events.Command.RemoveAccount:
                if self.db.remove_account(data):
                    self.players.remove_account(data)

            elif command == Events.Command.AddPlayer:
                if self.db.add_player(data):
                    self.players.add_player(data)

            elif command == Events.Command.RemovePlayer:
                if self.db.remove_player(data):
                    self.players.remove_player(data)

        self.queue.clear()


# region Detail

class PlayerCache(Emitter):

    def __init__(self):
        super().__init__()
        self.players = {}
        self.accounts = set()
        self.player_to_legend = {}
        self.account_to_player = {}
        self.account_to_legend_and_rank = {}
        self.legend_to_scores = defaultdict(list)

    def __iter__(self):
        return self.players.values().__iter__()

    def add_account(self, account: str):
        self.accounts.add(account)
        self.on_event(Events.Player.UpdatedAccounts, self.accounts)

    def remove_account(self, account: str):
        self.accounts.remove(account)
        self.on_event(Events.Player.UpdatedAccounts, self.accounts)

    def add_player(self, player: Player):
        self.players[player.name] = player
        self.on_event(Events.Player.UpdatedPlayers, self.players)

    def remove_player(self, player: Player):
        del self.players[player.name]
        self.on_event(Events.Player.UpdatedPlayers, self.players)

    def named(self, name: str) -> Player:
        return self.players.get(name, Nobody)

    def set_account(self, player: str, account: str):

        if player not in self.player_to_legend:
            return

        if player in self.account_to_player.values():
            self._delete_accounts_associated_to(player)

        if player:
            self.account_to_player[account] = player
        else:
            del self.account_to_player[account]

        self.on_event(Events.Player.UpdatedPlayerAccounts, self.account_to_player)

    def set_live_player(self, player: Player, legend: str):

        if legend:
            self.player_to_legend[player.name] = legend
        else:
            if player.name in self.player_to_legend:
                del self.player_to_legend[player.name]

            self._delete_accounts_associated_to(player.name)

        self.on_event(Events.Player.UpdatedLivePlayers, self.player_to_legend)

    def add_scores(self, scores: [(str, str, Score)]):

        self.legend_to_scores.clear()
        self.account_to_legend_and_rank.clear()
        for legend, account, score in scores:
            self.legend_to_scores[legend].append(score)
            self.account_to_legend_and_rank[account] = (legend, len(self.legend_to_scores[legend]))

        # If each player has a unique legend, accounts can be assumed based on legend order
        if self.has_unique_player_for_each_legend_and_score():
            for account, (legend, _) in self.account_to_legend_and_rank.items():
                players = [k for k, v in self.player_to_legend.items() if v == legend]
                self.account_to_player[account] = players[0]

    def get_scores(self) -> [(LivePlayer, Score)]:
        """
        For every n scores:
            -> get players with that legend
            -> get accounts with that legend
            -> For each score:
                -> get player of the account of the score
                -> associate player, legend and score
        :return:
        """
        all_scores = []

        for legend, scores in self.legend_to_scores.items():
            accounts = [k for k, v in self.account_to_legend_and_rank.items() if v[0] == legend]
            accounts.sort(key=lambda x: self.account_to_legend_and_rank[x][1])
            for i, score in enumerate(scores):
                player = self.account_to_player[accounts[i]]
                all_scores.append((LivePlayer(self.named(player), legend), score))

        return all_scores

    def has_player_for_each_legend_and_score(self) -> bool:
        # TODO: Only take scores of certain legends depending on mode

        # Each live player must have an account, legend and score
        if self.has_unique_player_for_each_legend_and_score():
            return True

        # For every n scores per legend in scores, check there is n players
        for legend, scores in self.legend_to_scores.items():
            if len(scores) != sum(legend == v for v in self.player_to_legend.values()):
                return False

        return True

    def has_unique_player_for_each_legend_and_score(self) -> bool:
        # Each live player must have an account, legend and score
        if all((len(v) == 1 and k in self.player_to_legend.values())
               for k, v in self.legend_to_scores.items()):
            return True
        return False

    def _delete_accounts_associated_to(self, player: str):
        for account, name in list(self.account_to_player.items()):
            if player == name:
                del self.account_to_player[account]

# endregion
