from fastapi import WebSocket
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Match as MatchDB
from app.src.models.base import Card as CardDB
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
            player = PlayerDB.get(id=player_id)
            return player
        
def get_card_by_id(card_id):
    with db_session:
        card = CardDB.get(id = card_id)
    return card

def discard_card_of_player(card_id,match_id,player_id):
    with db_session:
        player = get_player_by_id(player_id)
        card = get_card_by_id(card_id)

        if card != None:
            player.hand.remove(card)
        else:
             pass
        match = MatchDB.get(id = match_id)
        match.discard_pile.add(card)
        flush()
