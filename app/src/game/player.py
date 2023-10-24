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
    """
    Get player from db

    Args:
        player_id (int)

    Returns:
        player (Player)
    """
    with db_session:
        player = PlayerDB.get(id=player_id)
        return player


def get_card_by_id(card_id):
    """
    Get card from db

    Args:
        card_id (int)

    Returns:
        card (Card)
    """
    with db_session:
        card = CardDB.get(id=card_id)
    return card


def discard_card_of_player(card_id, match_id, player_id):
    """
    Discard a card from a player hand and add it to the discard pile

    Args:
        card_id (int)
        match_id (int)
        player_id (int)

    Returns:
        None
    """
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


"""
def get_card_image(path: str):
    with open(path, "rb") as f:
        card_img = base64.b64encode(f.read())
        f.close()
    return card_img
"""


def get_card_image(path: str):
    with open(path, "rb") as f:
        card_img = base64.b64encode(f.read()).decode(
            "utf-8"
        )  # Convertir a cadena de texto
    return card_img


@db_session
def get_card(match_id: int, player_id: int):
    """
    Get a card from the deck and add it to the player hand

    Args:
        match_id (int)
        player_id (int)

    Returns:
        card (Card)
    """
    match = MatchDB.get(id=match_id)
    player = PlayerDB.get(id=player_id)
    if match.deck == [] and match.discard_pile != []:
        deck = match.discard_pile.copy()
        match.discard_pile.clear()
        match.deck.add(deck)

    # se puede reutilizar para sospecha.
    card = select(c for c in match.deck).random(1)[0]
    card_image = get_card_image(card.image)
    player.hand.add(card)
    match.deck.remove(card)
    return {"id": card.id, "name": card.name, "image": card_image}


@db_session
def get_player_hand(match_id: int, player_id: int):
    """
    Get the cards of a player

    Args:
        match_id (int)
        player_id (int)

    Returns:
        hand (list of Card)
    """
    match = MatchDB.get(id=match_id)
    player = PlayerDB.get(id=player_id)
    hand = []

    cards = select(c for c in player.hand)[:]
    for card in cards:
        card_image = get_card_image(card.image)
        hand.append({"id": card.id, "name": card.name, "image": card_image})
    return hand


@db_session
def delete_player(player_id: int, match_id: int):
    """
    Delete a player from the match

    Args:
        player_id (int)
        match_id (int)

    Returns:
        None
    """

    match = MatchDB.get(id=match_id)
    player = PlayerDB.get(id=player_id)
    match.players.remove(player)
    match.number_players -= 1
    flush()


def is_player_main(match, player):
    return match.turn == player.position


def exchange(player_main, player_target, card_main):
    with db_session:
        player_target.hand.add(card_main)
        player_main.hand.remove(card_main)
    flush()
