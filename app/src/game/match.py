from typing import List
from fastapi import WebSocket
from pony.orm import *

from app.src.game.player import Player
from app.src.router.match_connection_manager import MatchConnectionManager
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB


# match tiene si o si owner, y si o si tiene 1 player
class Match:
    def __init__(
        self, player_name: str, match_name: str, max_players: int, min_players: int
    ):
        self._match_connection_manager = MatchConnectionManager()

        with db_session:
            player_db = PlayerDB(name=player_name)
            flush()
            self._player_owner_id = player_db.id

            match_db = MatchDB(
                name=match_name,
                number_players=1,
                max_players=max_players,
                min_players=min_players,
                started=False,
                finalized=False,
                turn=None,
                player_owner=player_db,
                players=[player_db],
            )
            flush()
            self._id = match_db.id

            # now that match is in db, update match player field
            player_db.match = match_db
            flush()

        MATCHS.append(self)


MATCHS: List[Match] = []
