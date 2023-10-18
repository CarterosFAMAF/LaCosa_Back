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
            started=False,
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

def test_valid_effect_LANZALLAMAS():
    with db_session:
        player = PlayerDB(name="player_in")

        flush()
        player_id = player.id
        player.position = 1
        player.role = "alive"
        flush()
        
        player_target = PlayerDB(name = 'player_target')

        flush()
        player_target_id = player_target.id
        player_target.position = 2
        player_target.role = "alive"
        flush()
        

        player_dead = PlayerDB(name = 'player_dead')
        flush()
        player_dead_id = player_dead.id
        player_dead.position = 3
        player_dead.role = "alive"
        flush()
        

        card = select (p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]

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
            players=[player,player_target,player_dead],
        )
        flush()
        match_id = match.id
        flush()
        add_cards_to_deck(match_id,4)

    with db_session:
        player = get_player_by_id(player_id)
        player_target = get_player_by_id(player_target_id)
        play_card(player,player_target,match_id,card_id)
        assert player_target.role == PLAYER_ROLE_DEAD
        assert player.hand == []
        next_turn(match_id)
        match_rec = get_match_by_id(match_id)
        assert match_rec.discard_pile.count() == 2
        assert match_rec.turn == 3

    
def test_valid_effect_Vigila_tus_espaldas():
    with db_session:
        
        player = PlayerDB(name = 'player')
        flush()
        player_id = player.id
        player.position = 0
        player.role = "alive"
        flush()
        
        player_1 = PlayerDB(name = 'player_target')
        flush()
        player_1_id = player_1.id
        player_1.position = 1
        player_1.role = "alive"
        flush()
        
        player_2 = PlayerDB(name = 'player_dead')
        flush()
        player_2_id = player_2.id
        player_2.position = 2
        player_2.role = "alive"
        flush()

        player_3 = PlayerDB(name = 'manolito')
        flush()
        player_3_id = player_3.id
        player_3.position = 3
        player_3.role = "alive"
        flush()

        card_vigila_tus_espaldas = select (p for p in CardDB if p.card_id == VIGILA_TUS_ESPALDAS).random(1)[0]
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

    with db_session:
        play_card(player,None,match_id,card_vigila_tus_espaldas_id)
        player = get_player_by_id(player_id)
        player_1 = get_player_by_id(player_1_id)
        player_2 = get_player_by_id(player_2_id)
        player_3 = get_player_by_id(player_3_id)
        assert player.position == 0
        assert player_1.position == 3
        assert player_2.position == 2
        assert player_3.position == 1


def test_valid_effect_MAS_VALE_QUE_CORRAS():
    with db_session:
        
        player = PlayerDB(name = 'player')
        flush()
        player_id = player.id
        player.position = 0
        player.role = "alive"
        flush()
        
        player_target = PlayerDB(name = 'player_target')
        flush()
        player_target_id = player_target.id
        player_target.position = 2
        player_target.role = "alive"
        flush()
        
        player_dead = PlayerDB(name = 'player_dead')
        flush()
        player_dead_id = player_dead.id
        player_dead.position = 1
        player_dead.role = "alive"
        flush()

        player_manolito = PlayerDB(name = 'manolito')
        flush()
        player_manolito_id = player_manolito.id
        player_manolito.position = 3
        player_manolito.role = "alive"
        flush()

        card_mas_vale_que_corras = select (p for p in CardDB if p.card_id == MAS_VALE_QUE_CORRAS).random(1)[0]
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
            players=[player,player_target,player_manolito,player_dead],
        )
        flush()
        match_id = match.id
        add_cards_to_deck(match_id,4)

    with db_session:
        player = get_player_by_id(player_id)
        player_target = get_player_by_id(player_target_id)
        play_card(player,player_target,match_id,card_mas_vale_que_corras_id)
        assert player.position == 2 
        assert player_target.position == 0

        play_card(player,player_target,match_id,card_mas_vale_que_corras_id)
        assert player.position == 0
