from pony.orm import *
from app.src.models.base import db
from app.src.game.constants import *
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.src.game.deck import add_cards_to_deck
from app.src.game.match import deal_cards, check_and_set_match_end
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
def test_check_and_set_match_end():
    player = PlayerDB(name="test_player")
    player.role = PLAYER_ROLE_HUMAN
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
    check_and_set_match_end(match.id)
    assert match.finalized == True
