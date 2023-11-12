from fastapi import WebSocket
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Match as MatchDB
from app.src.models.base import Card as CardDB

from app.src.game.constants import *

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
        card_img = base64.b64encode(f.read()).decode('utf-8')  # Convertir a cadena de texto
    return card_img


@db_session
def get_card(match_id: int, player_id: int,panic:bool=True):
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
    
    if match.letter_to_raise:
        with db_session:
            card = match.extra_deck #aca no se si lo copia pero vamo a ve
            match.extra_deck = None
            match.letter_to_raise = False
            flush()

    elif (panic):
        #cuando tengo que sacar una carta del mazo que no sea del tipo panico
        card = select(c for c in match.deck).random(1)[0]
        if card == None:
            #falta eliminar la carta de discard_pile
            card = select(c for c in match.discard_pile).random(1)[0]
            match.discard_pile.remove(card)
    else:
        card = select(c for c in match.deck if c.type != TYPE_PANIC).random(1)[0]
        
    card_image = get_card_image(card.image)
    player.hand.add(card)
    match.deck.remove(card)
    return {"id": card.id, "name": card.name, "image": card_image, "type": card.type}


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

    cards = select(c for c in player.hand if c.type != TYPE_PANIC)[:]
    for card in cards:
        card_image = get_card_image(card.image)
        hand.append(
            {"id": card.id, "name": card.name, "image": card_image, "type": card.type}
        )
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


def is_player_main_turn(match, player):
    """
    Returns True if is the player turn

    Args:
        match (Match)
        player (Player)

    Returns:
        bool
    """

    return match.turn == player.position


def get_next_player(match) -> PlayerDB:
    """
    Find the next player by turn in the match

    Args:
        match (Match)

    Returns:
        player (PlayerDB)
    """

    player = None

    turn = match.turn

    with db_session:
        while True:
            if match.clockwise:
                turn = (turn + 1) % match.number_players
            else:
                turn = (turn - 1) % match.number_players

            player = select(p for p in match.players if p.position == turn).first()
            # if it is not dead, break the loop, else, continue
            if player.role != PLAYER_ROLE_DEAD:
                break
    return player

def get_player_in_turn(match_id):
    with db_session:
        match = MatchDB.get(id=match_id)
        player_out_turn = select(p for p in match.players if p.position == 0).first()
    return player_out_turn

def get_next_player_by_player_turn(match_id, player_id):
    """
    Returns the next player from a specific player

    Args:
        match_id (int)
        player_id (int)
    
    Returns:
        player (PlayerDB)
    """
    player_out_turn = None
    #deberia fijarme el jugador que le sigue a player
    player = get_player_by_id(player_id)
    turn = player.position
    while True:
        with db_session:
            match = MatchDB.get(id=match_id)
            if match.clockwise:
                turn = (turn + 1) % match.number_players
            else:
                turn = (turn - 1) % match.number_players
            player_out_turn = select(p for p in match.players if p.position == turn).first()
            # if it is not dead, break the loop, else, continue
            if player_out_turn.role != PLAYER_ROLE_DEAD:
                break
    return player_out_turn

def prepare_exchange_card(player_main_id, card_id):
    """
    Discard card of main player and add it to the target player hand

    Args:
        player_main (Player)
        player_target (Player)
        card_main (Card)

    Returns:
        None
    """
    with db_session:
        player_main = PlayerDB.get(id=player_main_id)
        card = CardDB.get(id=card_id)
        
        player_main.card_exchange = card
        player_main.hand.remove(card)

        flush()


def apply_exchange(player_main_id, player_target_id):
    with db_session:
        player_main = get_player_by_id(player_main_id)
        player_target = get_player_by_id(player_target_id)
        card_main_id = player_main.card_exchange.id
        card_target_id = player_target.card_exchange.id
        player_main.hand.add(player_target.card_exchange)
        player_target.hand.add(player_main.card_exchange)
        player_main.card_exchange = None
        player_target.card_exchange = None
        flush()

    return card_main_id, card_target_id


def apply_effect_infeccion(player_target_id):
    """
    Change player role to infected

    Args:
        player_target_id (int)

    Return:
        None
    """
    with db_session:
        player_target = get_player_by_id(player_target_id)
        if player_target.role != PLAYER_ROLE_THE_THING:
            player_target = get_player_by_id(player_target_id)
            player_target.role = PLAYER_ROLE_INFECTED
            flush()
