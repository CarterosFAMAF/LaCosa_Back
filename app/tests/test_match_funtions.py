from pony.orm import *
from app.src.models.base import db
from app.src.game.constants import *
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.src.game.deck import add_cards_to_deck
from app.src.game.match import *
from app.src.game.constants import *


@db_session
def test_deal_card():
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
    assert player.hand.count() == 4
    assert [] != select(c for c in player.hand if c.card_id == LA_COSA)[:]


@db_session
def test_check_match_end():
    player1 = PlayerDB(name="test_player_1")
    player2 = PlayerDB(name="test_player_2")
    flush()
    match = MatchDB(
        name="test_match",
        number_players=2,
        max_players=12,
        min_players=4,
        started=True,
        finalized=False,
        turn=None,
        player_owner=player1,
        players=[player1,player2],
    )
    flush()
    player1.role = PLAYER_ROLE_HUMAN
    player2.role = PLAYER_ROLE_DEAD
    flush()
    status = check_match_end(match.id)
    assert status == WS_STATUS_HUMANS_WIN
    player1.role = PLAYER_ROLE_THE_THING
    player2.role = PLAYER_ROLE_DEAD
    flush()
    status = check_match_end(match.id)
    assert status == WS_STATUS_INFECTEDS_WIN
    player1.role = PLAYER_ROLE_THE_THING
    player2.role = PLAYER_ROLE_INFECTED
    flush()
    status = check_match_end(match.id)
    assert status == WS_STATUS_THE_THING_WIN
    player1.role = PLAYER_ROLE_THE_THING
    player2.role = PLAYER_ROLE_HUMAN
    flush()
    status = check_match_end(match.id)
    assert status == MATCH_CONTINUES
    
    
    