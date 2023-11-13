from pony.orm import *
from fastapi.testclient import TestClient
from app.tests.test_main import test_app
from app.src.models.base import db
from app.src.game.constants import *
from app.src.game.player import *
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.src.game.deck import add_cards_to_deck
from app.src.game.match import deal_cards


@db_session
def test_get_player_hand():
    player = PlayerDB(name="test_player")
    flush()
    match = MatchDB(
        name="test_match",
        number_players=4,
        max_players=12,
        min_players=4,
        started=False,
        finalized=False,
        turn=None,
        player_owner=player,
        players=[player],
    )
    flush()
    add_cards_to_deck(match.id, match.number_players)
    deal_cards(match.id)
    hand = get_player_hand(match.id, player.id)
    assert len(hand) == 4


@db_session
def test_delete_player():
    player = PlayerDB(name="test_player")
    flush()
    match = MatchDB(
        name="test_match",
        number_players=4,
        max_players=12,
        min_players=4,
        started=False,
        finalized=False,
        turn=None,
        player_owner=player,
        players=[player],
    )
    flush()
    delete_player(player.id, match.id)
    assert len(match.players) == 0
    
def test_get_player_by_id():
    with db_session:
        player = PlayerDB(name="test_player")
        flush()
        player2 = get_player_by_id(player.id)
        assert player.id == player2.id
        
def test_get_card_by_id():
    with db_session:
        lanzallamas = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]
        card = get_card_by_id(lanzallamas.id)
        assert lanzallamas.id == card.id
        
def test_discard_card_of_player():
    with db_session:
        player = PlayerDB(name="test_player")
        flush()
        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=None,
            player_owner=player,
            players=[player],
        )
        flush()
        lanzallamas = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]
        player.hand.add(lanzallamas)
        discard_card_of_player(lanzallamas.id, match.id, player.id)
        assert len(player.hand) == 0 and len(match.discard_pile) == 1
        
def test_get_card():
     with db_session:
        player = PlayerDB(name="test_player")
        flush()
        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=None,
            player_owner=player,
            players=[player],
        )
        flush()
        lanzallamas = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]
        match.deck.add(lanzallamas)
        get_card(match.id, player.id)
        assert len(match.deck) == 0 and len(player.hand) == 1
        whisky = select(p for p in CardDB if p.card_id == WHISKY).random(1)[0]
        match.discard_pile.add(whisky)
        get_card(match.id, player.id)
        assert len(match.deck) == 0 and len(match.discard_pile) == 0 and len(player.hand) == 2
        
def test_player_turns():
    with db_session:
        player0 = PlayerDB(name="test_player_0")
        player0.position = 0
        player0.role = PLAYER_ROLE_HUMAN
        player1 = PlayerDB(name="test_player_1")
        player1.position = 1
        player1.role = PLAYER_ROLE_HUMAN
        player2 = PlayerDB(name="test_player_2")
        player2.position = 2
        player2.role = PLAYER_ROLE_HUMAN
        player3 = PlayerDB(name="test_player_3")
        player3.position = 3
        player3.role = PLAYER_ROLE_HUMAN
        flush()
        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=True,
            finalized=False,
            turn=0,
            clockwise = True,
            player_owner=player0,
            players=[player0, player1, player2, player3],
        )
        flush()
        assert is_player_main_turn(match,player0)
        player_next_turn = get_next_player(match)
        assert player_next_turn.id == player1.id
        match.clockwise = False
        player_next_turn = get_next_player(match)
        assert player_next_turn.id == player3.id
        player_in_turn = get_player_in_turn(match.id)
        assert player_in_turn.id == player0.id
        player = get_next_player_by_player_turn(match.id, player0.id)
        assert player.id == player3.id
        match.clockwise = True
        player = get_next_player_by_player_turn(match.id, player0.id)
        assert player.id == player1.id


def test_exchange():
    with db_session:
        player = PlayerDB(name="test_player")
        player_target = PlayerDB(name="test_player_target")
        
        whisky = select(p for p in CardDB if p.card_id == WHISKY).random(1)[0]
        lanzallamas = select(p for p in CardDB if p.card_id == LANZALLAMAS).random(1)[0]
        player.hand.add(lanzallamas)
        player_target.hand.add(whisky)
        prepare_exchange_card(player.id, lanzallamas.id)
        prepare_exchange_card(player_target.id, whisky.id)
        assert len(player.hand) == 0 and player.card_exchange.id == lanzallamas.id
        assert len(player_target.hand) == 0 and player_target.card_exchange.id == whisky.id
        apply_exchange(player.id, player_target.id)
        assert len(player.hand) == 1 and player.card_exchange == None
        assert len(player_target.hand) == 1 and player_target.card_exchange == None

        apply_effect_infeccion(player_target.id)
        assert player_target.role == PLAYER_ROLE_INFECTED