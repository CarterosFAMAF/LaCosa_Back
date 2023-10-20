import json

from typing import List
from fastapi import WebSocket
from pony.orm import *

from app.src.game.player import *
from app.src.game.constants import *
from app.src.game.deck import *

from app.src.websocket.match_connection_manager import *

from app.src.models.base import Match as MatchDB
from app.src.models.base import Player as PlayerDB
from app.src.models.base import Card as CardDB


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


def join_match(player_name: str, match_id: int):
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

    player_db = None
    # add player to match
    with db_session:
        player_db = PlayerDB.get(id=player._id)
        player_db.role = PLAYER_ROLE_LOBBY
        match_db = MatchDB.get(id=match_id)
        match_db.players.add(player_db)
        match_db.number_players += 1
        flush()

    return {"player_id": player_db.id, "match_name": match_db.name}


def remove_player_from_match(player_id: int, match_id: int):
    """
    Remove a player from a match.
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
    return_match = None

    for match in MATCHES:
        print("DEBUG: match._id: " + str(match._id) + " match_id: " + str(match_id))
        print(match._id == match_id)
        if match._id == match_id:
            print("DEBUG: match found")
            return_match = match
            break
    print(return_match)
    return return_match


def get_match_by_id(match_id: int):
    """
    Get a match from db by id

    Args:
        match_id (int)

    Returns:
        match (Match)
    """
    match_db = None
    with db_session:
        match_db = MatchDB.get(id=match_id)
    return match_db


def next_turn(match_id: int):
    """
    Set the next turn in a match

    Args:
        match_id (int)

    Returns:
        None
    """
    with db_session:
        match = get_db_match_by_id(match_id)
        player = None

        while True:
            if match.clockwise:
                match.turn = ((match.turn + 1) % match.number_players)
            else:
                match.turn = ((match.turn - 1) % match.number_players)
            # get the player with the current turn
            flush()
            player = select(
                p for p in match.players if p.position == match.turn
            ).first()
            # if it is not dead, break the loop, else, continue
            if player.role != PLAYER_ROLE_DEAD:
                break

@db_session
def deal_cards(match_id: int):
    """
    Deal cards to players in a match

    Args:
        match_id (int)

    Returns:
        None
    """

    match = MatchDB.get(id=match_id)
    players_list = select(p for p in match.players)[:]
    
    for player in players_list:
        cards = select(c for c in match.deck).random(4)
        player.hand.add(cards)
        match.deck.remove(cards)
        
    the_thing_player = select(p for p in match.players).random(1)[0]
    card = select(p for p in the_thing_player.hand).random(1)
    
    the_thing_player.hand.remove(card)
    match.deck.add(card)
    card_the_thing = CardDB.get(card_id=LA_COSA)
    the_thing_player.hand.add(card_the_thing)
    the_thing_player.role = PLAYER_ROLE_THE_THING
    flush()


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


@db_session
def start_game(match_id: int):
    """
    Start a match
    anade las cartas al deck ,reparte las cartas , asigna posiciones

    Args:
        match_id (int)

    Returns:
        None
    """
    
    match = MatchDB.get(id=match_id)
    add_cards_to_deck(match_id, match.number_players)
    match.started = True
    match.clockwise = True
    match.turn = 0
    deal_cards(match_id)
    players = select(p for p in match.players).random(match.number_players)
    position = 0
    for player in players:
        player.position = position
        if player.role != PLAYER_ROLE_THE_THING:
            player.role = PLAYER_ROLE_HUMAN
        position += 1
    flush()


def end_match(match_id):
    """
    Set match to finalized in db, remove from live matches

    Args:
        match_id (int)

    Returns:
        None
    """
    with db_session:
        match = MatchDB.get(id=match_id)
        match.finalized = True
        flush()
    MATCHES.remove(get_live_match_by_id(match_id))


def delete_match(match_id):
    """
    Delete match from db

    Args:
        match_id (int)

    Returns:
        None
    """
    with db_session:
        match = MatchDB.get(id=match_id)
        match.delete()
        flush()


def check_and_set_match_end(match_id):
    """
    Check if match has ended
    Iterate over players and check if there is only one human player alive

    Args:
        match_id (int)

    Returns:
        ended (bool)
    """
    with db_session:
        match = MatchDB.get(id=match_id)
        players = select(p for p in match.players)[:]
        humans_alive = 0
        ended = False

        for player in players:
            if player.role == PLAYER_ROLE_HUMAN:
                humans_alive += 1

        if humans_alive == 1:
            ended = True
            end_match(match_id)

        else:
            ended = False

        return ended


MATCHES: List[Match] = []
