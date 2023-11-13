from fastapi import status
from pony.orm import *
from fastapi.testclient import TestClient
from app.src.models.base import db
from app.src.game.deck import add_cards_to_deck, create_deck
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.tests.test_main import test_app
from app.src.models.base import load_cards

client = TestClient(app=test_app)
load_cards()


@db_session
def test_add_cards_to_deck():
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
    assert match.deck.count() == 35

def test_add_cards_to_deck():
    deck = create_deck(4)
    assert len(deck) == 35
    deck = create_deck(5)
    assert len(deck) == 39
    deck = create_deck(6)
    assert len(deck) == 54
    deck = create_deck(7)
    assert len(deck) == 63
    deck = create_deck(8)
    assert len(deck) == 69
    deck = create_deck(9)
    assert len(deck) == 88
    deck = create_deck(10)
    assert len(deck) == 95
    deck = create_deck(11)
    assert len(deck) == 108
    deck = create_deck(12)
    assert len(deck) == 108
    deck = create_deck(13)
    assert len(deck) == 0