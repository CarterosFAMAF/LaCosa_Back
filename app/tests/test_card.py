from fastapi import status
from pony.orm import *
from fastapi.testclient import TestClient
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Card as CardDB
from app.main import app
from app.src.models.base import load_cards
from app.src.game.player import *
from app.src.game.match import *
from app.src.game.card import play_card
from app.src.game.deck import *
client = TestClient(app=app)

def test_valid_effect_LANZALLAMAS():
    with db_session:
        player = PlayerDB(name = 'player_in')
        flush()
        player_id = player.id
        player.turn = 1
        player.role = "alive"
        player_target = PlayerDB(name = 'player_target')
        flush()
        player_target_id = player_target.id
        player.turn = 2
        player_target.role = "alive"
        card = select (p for p in CardDB).random(1)[0]
        player.hand.add(card)

        match = MatchDB(
            name="test_match",
            number_players=4,
            max_players=12,
            min_players=4,
            started=False,
            finalized=False,
            turn=1,
            player_owner=player,
            players=[player],
        )
        flush()
        assert match.turn == 1
        match_id = match.id
        add_cards_to_deck(match_id,4)
    
    play_card(player_id,player_target_id,match_id,LANZALLAMAS)
    player = get_player_by_id(player_id)
    player_target = get_player_by_id(player_target_id)
    assert player_target.role == "dead"

    with db_session:
        next_turn(match_id)
        match_rec = MatchDB.get(id = match_id)
        assert match_rec.turn == 2
        assert match_rec.discard_pile.count() == 1
        