from fastapi import WebSocket
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Card as CardDB
from app.src.models.base import Match as MatchDB
from pony.orm import *
from app.src.game.player import *
from app.src.game.match import *
from app.src.game.constants import *


class Card:
    name: str


def play_card(player_in, player_out, match_id: int, card_id: int):
    """
    Play a card from a player to another player, changes the state of the game, and send a message to all players

    Args:
        player_in (Player)
        player_out (Player)
        match_id (int)
        card_id (int)

    Returns:
        None
    """
    card = get_card_by_id(card_id)
    assert card is not None
    status = None

    if card.card_id == LANZALLAMAS:
        status = play_lanzallamas(player_out.id, match_id)
    elif card.card_id == MAS_VALE_QUE_CORRAS:
        status = play_mas_vale_que_corras(player_in.id, player_out.id, match_id)
    elif card.card_id == VIGILA_TUS_ESPALDAS:
        status = play_vigila_tus_espaldas(match_id)
    elif card.card_id == CAMBIO_DE_LUGAR:
        status = play_cambio_de_lugar(player_in.id, player_out.id, match_id)
    elif card.card_id == SEDUCCION:
        status = play_seduccion()
    elif card.card_id == CITA_A_CIEGAS:
        status = play_blind_date()
    else:
        pass

    discard_card_of_player(card.id, match_id, player_in.id)
    return status


def play_lanzallamas(player_target_id, match_id):
    """
    Set the role of a player to dead

    Args:
        player_target_id (int)

    Returns:
        None
    """
    with db_session:
        match = get_match_by_id(match_id)
        player_target = get_player_by_id(player_target_id)
        player_target.role = "dead"
        for card in player_target.hand:
            discard_card_of_player(card.id, match_id, player_target.id)
        flush()
    status = WS_STATUS_PLAYER_BURNED
    return status


def play_mas_vale_que_corras(player_main_id, player_target_id, match_id):
    """
    Change the position of two players, and change the turn of the match

    Args:
        player_main_id (int)
        player_target_id (int)

    Returns:
        message of players that change position
    """
    with db_session:
        player_main = get_player_by_id(player_main_id)
        player_target = get_player_by_id(player_target_id)
        pos_tmp = player_main.position
        player_main.position = player_target.position
        player_target.position = pos_tmp
        match = get_match_by_id(match_id)
        match.turn = player_main.position
        flush()

    status = WS_STATUS_CHANGED_OF_PLACES
    return status


def play_cambio_de_lugar(player_main_id, player_target_id, match_id):
    with db_session:
        player_main = get_player_by_id(player_main_id)
        player_target = get_player_by_id(player_target_id)
        pos_tmp = player_main.position
        player_main.position = player_target.position
        player_target.position = pos_tmp
        match = get_match_by_id(match_id)
        match.turn = player_main.position
        flush()

    status = WS_STATUS_CHANGED_OF_PLACES
    return status


def play_vigila_tus_espaldas(match_id):
    """
    reverse all positions of the players

    Args:
        match_id(int)

    Returns:
        message that all positions were reversed
    """
    # Invierte todas las posiciones de los jugadores en la partida
    with db_session:
        match = get_match_by_id(match_id)
        match.clockwise = not match.clockwise
        flush()
    status = WS_STATUS_REVERSE_POSITION
    return status


def play_seduccion():
    status = WS_STATUS_SEDUCCION
    return status

#esto probablemente cambie.
def play_blind_date(player_id,card_id,match_id):
    #debo sacar el card_id del hand de player y del deck de match e intercambiar.
    player = get_player_by_id(player_id)
    card = get_card_by_id(card_id)
    match = get_match_by_id(match_id)
    status = WS_STATUS_BLIND_DATE
    with db_session:
        player.hand.remove(card)
        card_deck = match.deck.get()
        player.hand.add(card_deck)
        match.deck.remove(card)
        #sacar una carta del mazo
    return status


    
def play_card_investigation(player_main, player_target, card):
    """
    Devuelve las cartas respectivo a su tipo de carta de investigacion

    Args:
        player_main (Player)
        player_target (Player)
        card (Card)

    Returns:
        List of cards
    """
    cards_returns = []
    card_id = card.id
    if card.card_id == SOSPECHA:
        cards_returns = play_suspicions(player_target)
        """ 
        with db_session:
            card_random = select(c for c in player_target.hand).random(1)[0]
            card_image = get_card_image(card_random.image)
            card_to_return = {
                "id": card_random.id,
                "name": card_random.name,
                "image": card_image,
            }
            cards_returns.append(card_to_return)
            """

    elif card.card_id == ANALISIS:
        cards_returns = play_analisis(player_target)

    elif card.card_id == WHISKY or card.card_id == UPS or card.card_id == QUE_QUEDE_ENTRE_NOSOTROS:
        cards_returns = cards_in_hand_player(player_main,card_id)
    return cards_returns

def play_suspicions(player_target):
    cards_returns = []
    with db_session:
        card_random = select(c for c in player_target.hand).random(1)[0]
        card_image = get_card_image(card_random.image)
        card_to_return = {
            "id": card_random.id,
            "name": card_random.name,
            "image": card_image,
        }
        cards_returns.append(card_to_return)
    return cards_returns

def cards_in_hand_player(player_main,card_id):
    cards_returns = []
    with db_session:
            cards = select(c for c in player_main.hand if c.id != card_id)[:]
            for card in cards:
                card_image = get_card_image(card.image)
                cards_returns.append(
                    {"id": card.id, "name": card.name, "image": card_image}
                )
    return cards_returns

def play_analisis(player_target):
    cards_returns = []
    with db_session:
            cards = select(c for c in player_target.hand)[:]
            for card in cards:
                card_image = get_card_image(card.image)
                cards_returns.append(
                    {"id": card.id, "name": card.name, "image": card_image}
                )
    return cards_returns


def create_status_investigation(card):
    status = None

    if card.card_id == SOSPECHA:
        status = WS_STATUS_SUSPECT
    elif card.card_id == ANALISIS:
        status = WS_STATUS_ANALYSIS
    elif card.card_id == WHISKY:
        status = WS_STATUS_WHISKY
    elif card.card_id == UPS:
        status = WS_STATUS_UPS
    elif card.card_id == QUE_QUEDE_ENTRE_NOSOTROS:
        status = WS_STATUS_LET_IT_REMAIN_BETWEEN_US
    return status

def is_investigation_card(card):
    return (
        card.card_id == SOSPECHA or card.card_id == WHISKY or card.card_id == ANALISIS or card.card_id == UPS or card.card_id == QUE_QUEDE_ENTRE_NOSOTROS
    )

def is_card_infected(card):
    return card.card_id == INFECCION

def is_card_panic(card):
    return card.card_id == UPS or card.card_id == QUE_QUEDE_ENTRE_NOSOTROS or card.card_id == REVELACIONES or card.card_id == CITA_A_CIEGAS

def can_defend(player_target, card):
    can_defend = False
    cards = select(c for c in player_target.hand if c.id != card.id)[:]

    if card.card_id == LANZALLAMAS:
        for card in cards:
            if card.card_id == NADA_DE_BARBACOA:
                can_defend == True
    if card.card_id == CAMBIO_DE_LUGAR or MAS_VALE_QUE_CORRAS:
        for card in cards:
            if card.card_id == AQUI_ESTOY_BIEN:
                can_defend == True

    return can_defend

def effect_defense(player_main, player_target, card_main, card_target, match):
    if card_target.card_id == NADA_DE_BARBACOA:
        discard_card_of_player(card_main.id, match.id, player_main.id)
        discard_card_of_player(card_target.id, match.id, player_target.id)
        # broadcasteamos "{player_target} evito ser calzinado por {player_main}"

    if card_target.card_id == AQUI_ESTOY_BIEN:
        discard_card_of_player(card_main.id, match.id, player_main.id)
        discard_card_of_player(card_target.id, match.id, player_target.id)
        # broadcasteamos ""
