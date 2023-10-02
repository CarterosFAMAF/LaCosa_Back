import json

from typing import List
from fastapi import WebSocket
from pony.orm import *

from app.src.game.player import Player
from app.src.game.match_connection_manager import (
    MatchConnectionManager,
    create_ws_message,
)
from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB


class Match:
    _id: int
    _lobby_id: int
    _match_connection_manager: MatchConnectionManager
    _player_owner_id: int

    def __init__(
        self, player_name: str, match_name: str, max_players: int, min_players: int
    ):
        """
        Create a match in DB to store match state. A match object in memory is created too, that will be used to manage the websocket connections.

        Args:
            player_name (str)
            match_name (str)
            max_players (int)
            min_players (int)

        Returns:
            match (Match)
        """
        self._match_connection_manager = MatchConnectionManager()

        # create player in db
        player = Player(player_name)

        # set player owner id to return to client
        self._player_owner_id = player._id

        with db_session:
            player_db = PlayerDB.get(id=player._id)

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

            # set match id to return to client
            self._id = match_db.id

            # now that match is in db, update match player field
            player_db.match = match_db
            flush()

        self._lobby_id = len(MATCHES)
        MATCHES.append(self)


async def join_match(player_name: str, match_id: int):
    """
    Join a player to a match

    Args:
        player_name (str)
        match_id (int)

    Returns:
        player_id (int)
        match_name (str)
    """

    # create model player in the db
    player = Player(player_name)

    # add player to match
    with db_session:
        player_db = PlayerDB.get(id=player._id)
        match_db = MatchDB.get(id=match_id)
        match_db.players.add(player_db)
        match_db.number_players += 1
        flush()

    # send message to all players in the match
    msg = f"{player_name} se unio a la partida"
    ws_msg = create_ws_message(match_id, 0, msg)
    match = get_live_match_by_id(match_id)
    await match._match_connection_manager.broadcast_json(ws_msg)

    return {"player_id": player_db.id, "match_name": match_db.name}


def remove_player_from_match(player_id: int, match_id: int):
    """
    Remove a player from a match

    Args:
        player_id (int)
        match_id (int)

    Returns:
        None
    """
    with db_session:
        player_db = PlayerDB.get(id=player_id)
        match_db = MatchDB.get(id=match_id)
        match_db.players.remove(player_db)
        match_db.number_players -= 1
        flush()


def get_live_match_by_id(match_id: int):
    """
    Get a match from memory by id

    Args:
        match_id (int)

    Returns:
        match (Match)
    """
    for match in MATCHES:
        if match._id == match_id:
            return match
        else:
            return None


def get_db_match_by_id(match_id: int):
    """
    Get a match from de database by id
    
    Args:
        match_id (int)

    Returns:
        match (MatchDB)
    """

    with db_session:
        match = MatchDB.get(id=match_id)
        return match


MATCHES: List[Match] = []
