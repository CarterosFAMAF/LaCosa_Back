from fastapi import WebSocket
from app.src.models.base import Player as PlayerDB
from app.src.models.base import *
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
        
def discard_card_of_player(card_id,match_id,player_id):
    with db_session:
        player = get_player_by_id(player_id)
        card = Card.get(id = card_id)
        match = Match.get(id = match_id)

        #player.hand.remove(card)
        #match.discard_pile.add(card)
        flush()