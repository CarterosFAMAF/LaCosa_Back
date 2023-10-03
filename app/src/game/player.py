from fastapi import WebSocket
from src.models.base import Player as PlayerDB , Card , Match
from pony.orm import *


class Player:
    _id: None

    def __init__(self, name):
        with db_session:
            player_db = PlayerDB(name=name)
            flush()
            self._id = player_db.id

    def get_player_by_id(player_id):
        with db_session:
            player = Player.get(id=player_id)
            return player
        
    def discard_card_of_player(card_id,match_id,player_id):
        #deberia encontrar la carta del set de cartas del jugador
        with Database:
            player = Player.get(player_id)
            card = Card.get(card_id)
            match = Match.get(match_id)

            player.deck.remove(card)
            match.discard_deck.add(card)
            flush()