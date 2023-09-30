from typing import List
from fastapi import WebSocket
from src.game.card import Card
from app.src.game.player import Player
from app.src.router.match_connection_manager import MatchConnectionManager


class Match:
    def __init__(self, player_name, match_name, max_players, min_players):
        player = Player(player_name)

        self.id = len(MATCHS)
        self.name = match_name
        self.max_players = max_players
        self.min_players = min_players
        self.owner = player
        self.started = False
        self.finished = False
        self.turn = None
        self.deck = None
        self.discard_pile : List[Card] = []
        self.players: List[Player] = []
        self.match_connection_manager = MatchConnectionManager()    #Esto es para manejar los connect,etc.

        self.add_player(player)
        MATCHS.append(self)

    def add_player(self, player: Player):
        player.match = self
        player.id = len(self.players)
        self.players.append(player)


MATCHS: List[Match] = []


