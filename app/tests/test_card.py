from fastapi import status
from pony.orm import *
from fastapi.testclient import TestClient
from app.src.models.base import db
from app.main import app
from app.src.models.base import load_cards
from app.src.game.player import *
from app.src.game.match import *
from app.src.game.card import *
client = TestClient(app=app)

@db_session
def test_valid_play_card():
    with db_session:
        player = PlayerDB(name = 'player_in')
        flush()
        player_target = PlayerDB(name = 'player_target')
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

    play_card(player.id,player_target.id,match.id,3)
    flush()
    player_target = get_player_by_id(2)
    assert player_target.role != "dead"