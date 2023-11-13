from fastapi import status
from fastapi.testclient import TestClient
from pony.orm import *
from app.tests.test_main import test_app
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Match as MatchDB
from app.src.models.base import Card as CardDB
from app.src.game.constants import *
from app.src.game.player import *
from app.src.game.card import *
from app.src.game.deck import *

client = TestClient(app=test_app)


def test_get_card_invalid_match():
    response = client.get(
        "/matches/312321/players/213123/get_card",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_card_invalid_player():
    with db_session:
        player = PlayerDB(name="test_player")
        flush()
        match = MatchDB(
            name="match_name",
            number_players=1,
            max_players=4,
            min_players=12,
            started=True,
            finalized=False,
            turn=None,
            player_owner=player,
            players=[player],
        )
        flush()
        match_id = match.id
    response = client.get(
        "/matches/" + str(match_id) + "/players/1289/get_card",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@db_session
def test_get_card():
    card = select(c for c in CardDB).random(1)[0]
    player = PlayerDB(name="test_player")
    flush()
    match = MatchDB(
        name="match_name",
        number_players=1,
        max_players=4,
        min_players=12,
        started=False,
        finalized=False,
        turn=None,
        player_owner=player,
        players=[player],
    )
    flush()
    match.deck.add(card)
    print(match.deck)
    get_card(match.id, player.id)
    assert match.deck == []
    assert player.hand.count() == 1


@db_session
def test_get_card_empty_deck():
    card = select(c for c in CardDB).random(2)
    player = PlayerDB(name="test_player")
    flush()
    match = MatchDB(
        name="match_name",
        number_players=1,
        max_players=4,
        min_players=12,

        started=False,
        finalized=False,
        turn=None,
        player_owner=player,
        players=[player],
    )
    flush()
    match.discard_pile.add(card)
    print(match.deck)
    get_card(match.id, player.id)
    assert match.discard_pile == []
    assert player.hand.count() == 1
    assert match.deck.count() == 1

# Tests of efects of cards
    """
def test_valid_effect():
    with db_session:
        player = PlayerDB(name="player_in")

        flush()
        player_id = player.id
        player.position = 1
        player.role = PLAYER_ROLE_HUMAN
        flush()

        player_target = PlayerDB(name="player_target")
        flush()
        player_target_id = player_target.id
        player_target.position = 2
        player_target.role = PLAYER_ROLE_HUMAN
        flush()
        

        player_dead = PlayerDB(name="player_dead")
        flush()
        player_dead_id = player_dead.id
        player_dead.position = 3
        player_dead.role = PLAYER_ROLE_HUMAN
        flush()

        card = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]

        card_id = card.id
        player.hand.add(card)

        flush()
        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=1,
            player_owner=player,
            players=[player, player_target, player_dead],
        )
        flush()

        match_id = match.id
        flush()
        add_cards_to_deck(match_id, 4)

    with db_session:
        player = get_player_by_id(player_id)
        player_target = get_player_by_id(player_target_id)
        play_card(player, player_target, match_id, card_id)

        assert player_target.role == PLAYER_ROLE_DEAD
        assert player.hand == []
        next_turn(match_id)
        match_rec = get_match_by_id(match_id)
        assert match_rec.discard_pile.count() == 2
        assert match_rec.turn == 3
    """


def test_valid_effect_Vigila_tus_espaldas():
    with db_session:
        player = PlayerDB(name="player")
        flush()
        player_id = player.id
        player.position = 0
        player.role = PLAYER_ROLE_HUMAN
        flush()

        player_1 = PlayerDB(name="player_target")
        flush()
        player_1_id = player_1.id
        player_1.position = 1
        player_1.role = PLAYER_ROLE_HUMAN
        flush()

        player_2 = PlayerDB(name="player_dead")
        flush()
        player_2_id = player_2.id
        player_2.position = 2
        player_2.role = PLAYER_ROLE_HUMAN
        flush()

        player_3 = PlayerDB(name="manolito")
        flush()
        player_3_id = player_3.id
        player_3.position = 3
        player_3.role = PLAYER_ROLE_HUMAN
        flush()

        card_vigila_tus_espaldas = select(
            p for p in CardDB if p.card_id == VIGILA_TUS_ESPALDAS
        ).random(1)[0]
        card_vigila_tus_espaldas_id = card_vigila_tus_espaldas.id
        player.hand.add(card_vigila_tus_espaldas)
        flush()

        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=0,
            player_owner=player,
            players=[player,player_1,player_2,player_3],
        )
        flush()
        match_id = match.id
        add_cards_to_deck(match_id,4)

        play_card(player,None,match_id,card_vigila_tus_espaldas_id)
        match.clockwise = False

def test_valid_effect_MAS_VALE_QUE_CORRAS():
    with db_session:
        
        player = PlayerDB(name = 'player')
        flush()
        player_id = player.id
        player.position = 0
        player.role = PLAYER_ROLE_HUMAN
        flush()

        player_target = PlayerDB(name="player_target")
        flush()
        player_target_id = player_target.id
        player_target.position = 2
        player_target.role = PLAYER_ROLE_HUMAN
        flush()

        player_dead = PlayerDB(name="player_dead")
        flush()
        player_dead_id = player_dead.id
        player_dead.position = 1
        player_dead.role = PLAYER_ROLE_HUMAN
        flush()

        player_manolito = PlayerDB(name="manolito")
        flush()
        player_manolito_id = player_manolito.id
        player_manolito.position = 3
        player_manolito.role = PLAYER_ROLE_HUMAN
        flush()

        card_mas_vale_que_corras = select(
            p for p in CardDB if p.card_id == MAS_VALE_QUE_CORRAS
        ).random(1)[0]
        card_mas_vale_que_corras_id = card_mas_vale_que_corras.id
        player.hand.add(card_mas_vale_que_corras)
        flush()

        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=0,
            player_owner=player,
            players=[player, player_target, player_manolito, player_dead],
        )
        flush()
        match_id = match.id
        add_cards_to_deck(match_id, 4)

    with db_session:
        player = get_player_by_id(player_id)
        player_target = get_player_by_id(player_target_id)
        play_card(player, player_target, match_id, card_mas_vale_que_corras_id)
        assert player.position == 2
        assert player_target.position == 0

        play_card(player, player_target, match_id, card_mas_vale_que_corras_id)
        assert player.position == 0

def test_valid_effect_cuarentena_hacha():
    with db_session:
        player = PlayerDB(name="player")
        player.position = 0
        player.role = PLAYER_ROLE_HUMAN
        flush()
        player_target= PlayerDB(name="player_target")
        player_target.position = 1
        player_target.role = PLAYER_ROLE_HUMAN
        flush()
        hacha = select(p for p in CardDB if p.card_id == HACHA).random(1)[0]
        cuarentena = select(p for p in CardDB if p.card_id == CUARENTENA).random(1)[0]
        player.hand.add(hacha)
        player.hand.add(cuarentena)
        flush()

        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=0,
            player_owner=player,
            players=[player,player_target],
        )
        flush()
        match_id = match.id
        add_cards_to_deck(match_id,4)

        play_card(player,player_target,match_id,cuarentena.id)
        assert player_target.quarantine == 3
        play_card(player,player_target,match_id,hacha.id)
        assert player_target.quarantine == 0
        

def test_valid_effect_cambio_de_lugar():
    with db_session:
        player = PlayerDB(name="player")
        player.position = 0
        player.role = PLAYER_ROLE_HUMAN
        flush()
        player_target= PlayerDB(name="player_target")
        player_target.position = 1
        player_target.role = PLAYER_ROLE_HUMAN
        flush()
        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=0,
            player_owner=player,
            players=[player,player_target],
        )
        flush()
        match_id = match.id
        add_cards_to_deck(match_id,4)
        
        cambio_de_lugar = select(p for p in CardDB if p.card_id == CAMBIO_DE_LUGAR).random(1)[0]
        lanzallamas = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]
        player.hand.add(lanzallamas)
        player.hand.add(cambio_de_lugar)
        
        play_card(player,player_target,match_id,cambio_de_lugar.id)
        assert player_target.position == 0
        assert player.position == 1
        play_card(player,player_target,match_id,lanzallamas.id)
        assert player_target.role == PLAYER_ROLE_DEAD
    
        
def test_create_status():
    with db_session:
        sospecha = select(p for p in CardDB if p.card_id == SOSPECHA).random(1)[0]
        analisis  = select(p for p in CardDB if p.card_id == ANALISIS).random(1)[0]
        whisky = select(p for p in CardDB if p.card_id == WHISKY).random(1)[0]
        assert WS_STATUS_SUSPECT == create_status_investigation(sospecha)
        assert WS_STATUS_ANALYSIS == create_status_investigation(analisis)
        assert WS_STATUS_WHISKY == create_status_investigation(whisky)
        assert create_card_exchange_message(sospecha.id) != {}
 
def test_play_car_investigation():
    with db_session:
        player = PlayerDB(name="player")
        player.position = 0
        player.role = PLAYER_ROLE_HUMAN
        flush()
        player_target= PlayerDB(name="player_target")
        player_target.position = 1
        player_target.role = PLAYER_ROLE_HUMAN
        flush()
        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=0,
            player_owner=player,
            players=[player,player_target],
        )
        flush()
        match_id = match.id
        add_cards_to_deck(match_id,4)

        sospecha = select(p for p in CardDB if p.card_id == SOSPECHA).random(1)[0]
        analisis  = select(p for p in CardDB if p.card_id == ANALISIS).random(1)[0]
        whisky = select(p for p in CardDB if p.card_id == WHISKY).random(1)[0]
        lanzallamas = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(2)[:]
        player.hand.add(whisky)
        player.hand.add(analisis)
        player.hand.add(sospecha)
        player.hand.add(lanzallamas)
        player_target.hand.add(lanzallamas)
        print(len(player_target.hand))

        cards = play_card_investigation(player,player_target,sospecha)
        assert len(cards) == 1
        cards = play_card_investigation(player,player_target,analisis)
        assert len(cards) == 2
        cards = play_card_investigation(player,player_target,whisky)
        assert len(cards) == 4
        assert is_investigation_card(whisky)
        assert is_investigation_card(analisis)
        assert is_investigation_card(sospecha)
        
       
def test_can_defense():
    with db_session:
        player = PlayerDB(name="player")
        player.position = 0
        player.role = PLAYER_ROLE_HUMAN
        flush()
        match = MatchDB(
            name="test_match",
            number_players=12,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=0,
            player_owner=player,
            players=[player],
        )
        flush()
        match_id = match.id
        add_cards_to_deck(match_id,12)

        aterrador = select(p for p in CardDB if p.card_id == ATERRADOR).random(1)[0]
        no_gracias = select(p for p in CardDB if p.card_id == NO_GRACIAS).random(1)[0]
        fallaste = select(p for p in CardDB if p.card_id == FALLASTE).random(1)[0]
        lanzallamas = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]
        nada_de_barbacoas = select(p for p in CardDB if p.card_id == NADA_DE_BARBACOAS).random(1)[0]
        cambio_de_lugar = select(p for p in CardDB if p.card_id == CAMBIO_DE_LUGAR).random(1)[0]
        mas_vale_que_corras = select(p for p in CardDB if p.card_id == MAS_VALE_QUE_CORRAS).random(1)[0]
        aca_estoy_bien = select(p for p in CardDB if p.card_id == AQUI_ESTOY_BIEN).random(1)[0]
        
        
        defend , cards = can_defend(0, 0)
        assert defend == False and len(cards) == 0
        player.hand.add(aterrador)
        defend , cards = can_defend(player.id, 0)
        assert defend == True and len(cards) == 1
        player.hand.add(no_gracias)
        defend , cards = can_defend(player.id, 0)
        assert defend == True and len(cards) == 2
        player.hand.add(fallaste)
        defend , cards = can_defend(player.id, 0)
        assert defend == True and len(cards) == 3
        defend , cards = can_defend(player.id, cambio_de_lugar.card_id)
        assert defend == False and len(cards) == 0
        defend , cards = can_defend(player.id, mas_vale_que_corras.card_id)
        assert defend == False and len(cards) == 0
        player.hand.add(aca_estoy_bien)
        defend , cards = can_defend(player.id, mas_vale_que_corras.card_id)
        assert defend == True and len(cards) == 1
        defend , cards = can_defend(player.id, mas_vale_que_corras.card_id)
        assert defend == True and len(cards) == 1
        player.hand.add(nada_de_barbacoas)
        defend , cards = can_defend(player.id, lanzallamas.card_id)
        assert defend == True and len(cards) == 1
        
def test_infected_card():
    with db_session:
        infectation = select(p for p in CardDB if p.card_id == INFECCION).random(1)[0]
        assert send_infected_card(infectation)
        
        player = PlayerDB(name="player")
        player.card_exchange = infectation
        flush()
        
        assert receive_infected_card(player.id)
         
def test_play_card_defense():
    with db_session:
        player = PlayerDB(name="player")
        player.position = 0
        player.role = PLAYER_ROLE_HUMAN
        flush()
        player_target= PlayerDB(name="player_target")
        player_target.position = 1
        player_target.role = PLAYER_ROLE_HUMAN
        flush()
        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=True,
            finalized=False,
            turn=0,
            player_owner=player,
            players=[player,player_target],
        )
        flush()
        add_cards_to_deck(match.id,10) 
       
        nada_de_barbacoas = select(p for p in CardDB if p.card_id == NADA_DE_BARBACOAS).random(1)[0]
        aca_estoy_bien = select(p for p in CardDB if p.card_id == AQUI_ESTOY_BIEN).random(1)[0]
        no_gracias = select(p for p in CardDB if p.card_id == NO_GRACIAS).random(1)[0]
        aterrador = select(p for p in CardDB if p.card_id == ATERRADOR).random(1)[0]
        lanzallamas = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]
        fallaste = select(p for p in CardDB if p.card_id == FALLASTE).random(1)[0]
        
        player.hand.add([nada_de_barbacoas,aca_estoy_bien,no_gracias,aterrador])

        status, list_card = play_card_defense(player.id, player_target.id, nada_de_barbacoas.id, match.id)
        assert status == WS_STATUS_NOTHING_BARBECUE and list_card == []
        
        status, list_card = play_card_defense(player.id, player_target.id, aca_estoy_bien.id, match.id)
        assert status == WS_STATUS_HERE_IM_FINE and list_card == []
        
        player_target.card_exchange = lanzallamas
        status, list_card = play_card_defense(player.id, player_target.id, no_gracias.id, match.id)
        assert status == WS_STATUS_NOPE_THANKS and len(list_card) == 1
        assert len(player_target.hand) == 1 and player.card_exchange == None
        player_target.card_exchange = fallaste
        status, list_card = play_card_defense(player.id, player_target.id, aterrador.id, match.id)
        assert status == WS_STATUS_SCARY and len(list_card) == 1
        assert len(player_target.hand) == 2 and player.card_exchange == None
        
