from fastapi import WebSocket
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Match as MatchDB
from pony.orm import *
import base64


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


def get_card_image(path:str):
    with open(path, 'rb') as f:
        card_img = base64.b64encode(f.read())
        f.close()
    return str(card_img)



@db_session
def get_card(match_id: int,player_id:int):
    match = MatchDB.get(id=match_id)
    player = PlayerDB.get(id=player_id)
    card_out= {}
    if player != None and match != None:
        card = select(c for c in match.deck).random(1)
        if card != []:
            player.hand.add(card)
            match.deck.remove(card)
            card_image = get_card_image(card.image)
            card_out={
                "card_id": card.card_id,
                "name": card.name,
                "image": card_image,
            }
    return card_out
