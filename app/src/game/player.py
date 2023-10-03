from fastapi import WebSocket
from src.models.base import Player as PlayerDB , Card , Match
from pony.orm import *


class Player:
    _id: None

def get_player_by_id(player_id):
    with db_session:
        player = Player.get(id=player_id)
        return player
        
def discard_card_of_player(card_id,match_id,player_id):
    with db_session:
        player = Player.get(player_id)
        card = Card.get(card_id)
        match = Match.get(match_id)

        player.deck.remove(card)
        match.discard_deck.add(card)
        flush()