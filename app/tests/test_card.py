from fastapi import status
from pony.orm import *
from fastapi.testclient import TestClient
from src.models.base import Player as PlayerDB
from src.models.base import Match as MatchDB
from main import app
from src.models.base import load_cards
from src.game.player import *
from src.game.match import *
from src.game.card import *
client = TestClient(app=app)

@db_session
def test_valid_effect_LANZALLAMAS():
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

    play_lanzallamas(player_target.id)
    flush()
    player_target = get_player_by_id(2)
    assert player_target.role != "dead"