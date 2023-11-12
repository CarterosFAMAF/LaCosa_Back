from fastapi import WebSocket
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Card as CardDB
from app.src.models.base import Match as MatchDB
from pony.orm import *
from app.src.game.player import *
from app.src.game.match import *
from app.src.game.constants import *
from app.src.websocket.constants import *


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
        status = WS_STATUS_SEDUCCION
    elif card.card_id == CITA_A_CIEGAS:
        status = WS_STATUS_BLIND_DATE
    elif card.card_id == REVELACIONES:
        status = WS_STATUS_REVELATIONS
    else:
        pass

    discard_card_of_player(card_id, match_id, player_in.id)
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
        player_target.role = PLAYER_ROLE_DEAD
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
    Reverse clockwise

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

  
def send_card_extra_deck(player_id,card_id,match_id):
    #cuando se usa intercambio
    with db_session:
        player = get_player_by_id(player_id)
        card = get_card_by_id(card_id)
        match = get_match_by_id(match_id)
        match.letter_to_raise = True
        match.extra_deck = card
        player.hand.remove(card)
        flush()
    

def play_card_investigation(player_main, player_target, card,match):
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
                "type" : card_random.type
            }
            cards_returns.append(card_to_return)
            """

    elif card.card_id == ANALISIS:
        cards_returns = play_analisis(player_target)

    elif (
        card.card_id == WHISKY
        or card.card_id == UPS
        or card.card_id == QUE_QUEDE_ENTRE_NOSOTROS
    ):
        cards_returns = cards_in_hand_player(player_main, card_id)
    elif card.card_id == DETERMINACION:
        cards_returns = play_determination(player_main, match)
    return cards_returns


def play_determination(player_main, match):
    cards_random = []
    with db_session:
        cards_random = select(c for c in match.deck if c.type != TYPE_PANIC).random(3)[
            :
        ]
        for card in cards_random:
            player_main.hand.add(card)
            match.deck.remove(card)
            match.discard_pile.add(card)
            flush()
    return cards_random


def play_suspicions(player_target):
    cards_returns = []
    with db_session:
        card_random = select(c for c in player_target.hand).random(1)[0]
        card_image = get_card_image(card_random.image)
        card_to_return = {
            "id": card_random.id,
            "name": card_random.name,
            "image": card_image,
            "type": card_random.type,
        }
        cards_returns.append(card_to_return)
    return cards_returns


def cards_in_hand_player(player_main, card_id):
    cards_returns = []
    with db_session:
        cards = select(c for c in player_main.hand if c.id != card_id)[:]
        for card in cards:
            card_image = get_card_image(card.image)
            cards_returns.append(
                {
                    "id": card.id,
                    "name": card.name,
                    "image": card_image,
                    "type": card.type,
                }
            )
    return cards_returns


def play_analisis(player_target):
    cards_returns = []
    with db_session:
        cards = select(c for c in player_target.hand)[:]
        for card in cards:
            card_image = get_card_image(card.image)
            cards_returns.append(
                {
                    "id": card.id,
                    "name": card.name,
                    "image": card_image,
                    "type": card.type,
                }
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
    elif card.card_id == DETERMINACION:
        status = WS_STATUS_DETERMINATION
    return status


def is_investigation_card(card):
    return (
        card.card_id == SOSPECHA
        or card.card_id == WHISKY
        or card.card_id == ANALISIS
        or card.card_id == UPS
        or card.card_id == QUE_QUEDE_ENTRE_NOSOTROS
        or card.card_id == DETERMINACION
    )


# DEFENSE


def can_defend(player_target_id, card_action):
    """
    From specific card and player, return if the player can defend with a defense card

    Args:
        player_target_id (int)
        card (Card)

    Returns:
        Bool
    """
    player_target = get_player_by_id(player_target_id)
    can_defend = False
    list_id_cards = []
    if player_target_id == 0:
        return can_defend , list_id_cards
    
    with db_session:
            cards = select(c for c in player_target.hand)[:]
            
    if card_action == 0:
        #casos para intercambio, no tenemos id de card_action
        for card in cards:
            if card.card_id == ATERRADOR or card.card_id == NO_GRACIAS or card.card_id == FALLASTE:
                can_defend = True
                list_id_cards.append(card.id)
    else:
        if card_action == LANZALLAMAS:
            for card in cards:
                if card.card_id == NADA_DE_BARBACOAS:
                    can_defend = True     
                    list_id_cards.append(card.id)
                    
        elif card_action == CAMBIO_DE_LUGAR or card_action == MAS_VALE_QUE_CORRAS:
            for card in cards:
                if card.card_id == AQUI_ESTOY_BIEN:
                    can_defend = True
                    list_id_cards.append(card.id)
    
    return can_defend,list_id_cards

def send_infected_card(card):
    return card.card_id == INFECCION

def receive_infected_card(player_id):
    with db_session:
        player = get_player_by_id(player_id)
        card = player.card_exchange
        is_infected = card.card_id == INFECCION
        return is_infected

def exist_infection(hand):
    infected = False
    infected_card_id = None
    for elem in hand:
        if elem["name"] == "Infeccion":
            infected = True
            infected_card_id = elem["id"]
    return infected,infected_card_id

    
def play_card_defense(player_main_id, player_target_id, card_id, match_id):
    """
    Play a card from a player to another player, changes the state of the game, and send a message to all players

    Args:
        player_main_id (int)
        player_target_id (int)
        card_id (int)
        match_id (int)

    Returns:
        None
    """
    # aclaracion de uso: player_main es jugador en turno y player_target_id es quien va a jugar carta def
    card = get_card_by_id(card_id)
    list_card = []
    assert card is not None
    status = None


    if card.card_id == NADA_DE_BARBACOAS:
        status = WS_STATUS_NOTHING_BARBECUE
    elif card.card_id == AQUI_ESTOY_BIEN:
        status = WS_STATUS_HERE_IM_FINE
    elif card.card_id == NO_GRACIAS:
        status,list_card = play_no_gracias(player_target_id)
    elif card.card_id == ATERRADOR:
        status,list_card = play_aterrador(player_target_id)
    else:
        raise Exception("Defense card not found")

    discard_card_of_player(card.id, match_id, player_main_id)
    
    return status, list_card


def play_aterrador(player_main_id):
    list_card = []
    status = WS_STATUS_SCARY
    with db_session:
        player_main = get_player_by_id(player_main_id)
        card_image = get_card_image(player_main.card_exchange.image)
        list_card.append(
                    {"id": player_main.card_exchange.id, 
                     "name": player_main.card_exchange.name, 
                     "image": card_image,
                     "type" : player_main.card_exchange.type
                     }
                )
        player_main.hand.add(player_main.card_exchange)
        player_main.card_exchange = None
        flush()
    return status, list_card


def play_no_gracias(player_main_id):
    card_return = []
    status = WS_STATUS_NOPE_THANKS
    with db_session:
        player_main = get_player_by_id(player_main_id)
        player_main.hand.add(player_main.card_exchange)
        card_image = get_card_image(player_main.card_exchange.image)
        card_return.append(
                    {"id": player_main.card_exchange.id, 
                     "name": player_main.card_exchange.name, 
                     "image": card_image,
                     "type" : player_main.card_exchange.type
                     }
                )
        player_main.card_exchange = None
        flush()
        
    return status,card_return


def play_aqui_estoy_bien(player_main_id, player_target_id, match_id):
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

    status = WS_STATUS_HERE_IM_FINE
    return status


def create_card_exchange_message(card_id):
    card = get_card_by_id(card_id)
    card_image = get_card_image(card.image)

    card_ws = {
        "id" : card.id ,
        "name" : card.name,
        "image" : card_image,
        "type" : card.type
    }
    
    response = {
        "status" : WS_CARD,
        "card" : card_ws
    }
    
    return response
