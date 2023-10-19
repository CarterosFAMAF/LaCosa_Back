from fastapi import WebSocket
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Match as MatchDB
from app.src.models.base import Card as CardDB
from app.src.models.schemas import *
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


def get_card_by_id(card_id):
    with db_session:
        card = CardDB.get(id=card_id)
    return card


def discard_card_of_player(card_id, match_id, player_id):
    with db_session:
        player = get_player_by_id(player_id)
        card = get_card_by_id(card_id)

        if card != None:
            player.hand.remove(card)
        else:
            pass
        match = MatchDB.get(id=match_id)
        match.discard_pile.add(card)
        flush()


def get_card_image(path: str):
    with open(path, "rb") as f:
        card_img = base64.b64encode(f.read())
        f.close()
    return card_img


@db_session
def get_card(match_id: int, player_id: int):
    match = MatchDB.get(id=match_id)
    player = PlayerDB.get(id=player_id)
    if match.deck == [] and match.discard_pile != []:
        deck = match.discard_pile.copy()
        match.discard_pile.clear()
        match.deck.add(deck)

#se puede reutilizar para sospecha.
    card = select(c for c in match.deck).random(1)[0]
    card_image = get_card_image(card.image)
    player.hand.add(card)
    match.deck.remove(card)
    return {"id": card.id, "name": card.name, "image": card_image}


@db_session
def get_player_hand(match_id: int, player_id: int):
    match = MatchDB.get(id=match_id)
    player = PlayerDB.get(id=player_id)
    hand = []

    cards = select(c for c in player.hand)[:]
    for card in cards:
        card_image = get_card_image(card.image)
        hand.append({"id": card.id, "name": card.name, "image": card_image})
    return hand
