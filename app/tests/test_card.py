from fastapi import status
from fastapi.testclient import TestClient
from pony.orm import *
from app.tests.test_main import test_app
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Match as MatchDB
from app.src.models.base import Card as CardDB
from app.src.game.constants import *
from app.src.game.player import *

client = TestClient(app=test_app)


def test_get_card_invalid_match():
    response = client.get(
            "/matches/312321/players/213123/get_card",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_card_invalid_player():
    with db_session:
        player = PlayerDB(
            name= "test_player"
        )
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
            "/matches/"+str(match_id)+"/players/1289/get_card",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@db_session
def test_get_card():
    card = select(c for c in CardDB).random(1)[0]
    player = PlayerDB(
        name= "test_player"
    )
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
    get_card(match.id,player.id)
    assert match.deck == []
    assert player.hand.count() == 1


@db_session
def test_get_card_empty_deck():
    card = select(c for c in CardDB).random(2)
    player = PlayerDB(
        name= "test_player"
    )
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
    get_card(match.id,player.id)
    assert match.discard_pile == []
    assert player.hand.count() == 1
    assert match.deck.count() == 1
