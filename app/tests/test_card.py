from fastapi import status
from fastapi.testclient import TestClient
from pony.orm import *
from app.tests.test_main import test_app
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Match as MatchDB
from app.src.models.base import Card as CardDB
from app.src.game.constants import *

client = TestClient(app=test_app)


def test_get_card_invalid_match():
    response = client.get(
            "/matches/312321/players/213123/get_card",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_card_invalid_player():
    with db_session:
        match = MatchDB(
            name="test_match",
            number_players=1,
            max_players=4,
            min_players=12,
            started=False,
            finalized=False,
            turn=None,
            player_owner=None,
            players=None,
        )
        flush()
        match_id = match.id
    response = client.get(
            "/matches/"+match_id+"/players/1289/get_card",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@db_session
def test_get_card():
    card = CardDB.get(card_id=LANZALLAMAS)
    player = PlayerDB(
        name= "test_player"
    )
    player.hand.add(card)
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
        deck=[card]
    )
    flush()
    get_card(match.id,player.id)

    assert match.deck.count() == 0
    assert player.hand.count() == 1
