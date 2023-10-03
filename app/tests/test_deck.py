from fastapi import status
from pony.orm import *
from fastapi.testclient import TestClient
from app.src.models.base import db
from app.src.game.deck import add_cards_to_deck
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.main import app
from app.src.models.base import load_cards

client = TestClient(app=app)
load_cards()

@db_session
def test_add_cards_to_deck():
    player = PlayerDB(name='test_player')
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
