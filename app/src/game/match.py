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


def list_not_started_matches() -> list:
    """
    Return a list of ListMatchOut objects with all the matches that are not started.

    Args:
        None

    Returns:
        matches (List[ListMatchOut])
    """
    matches_db = None
    matches_out = []

    with db_session:
        matches_db = select(m for m in MatchDB if m.started == False)[:]

        if matches_db is not None:
            for match_db in matches_db:
                match_out = ListMatchOut(
                    match_id=match_db.id,
                    match_name=match_db.name,
                    owner_name=match_db.player_owner.name,
                    player_count=match_db.number_players,
                    player_min=match_db.min_players,
                    player_max=match_db.max_players,
                    joined_players=[player.name for player in match_db.players],
                )

                matches_out.append(match_out)

    return matches_out


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
        if match._id == match_id:
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
                match.turn = (match.turn + 1) % match.number_players
            else:
                match.turn = (match.turn - 1) % match.number_players
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
        cards = select(c for c in match.deck if c.type != TYPE_PANIC).random(4)
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


def delete_live_match(match_id):
    """
    Delete match from live matches

    Args:
        match_id (int)

    Returns:
        None
    """
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

def check_match_end(match_id):
    """
    Check if match has ended
    Iterate over players and check if the thing is alive or if all the humans are infected 

    Args:
        match_id (int)

    Returns:
        msg (str)
    """
    with db_session:
        match = MatchDB.get(id=match_id)
        players = select(p for p in match.players)[:]
        humans_alive = 0
        the_thing_is_alive = False
        infeteds_alive = 0
        dead_players = 0
        ended = False

        for player in players:
            if player.role == PLAYER_ROLE_DEAD:
                dead_players += 1
            if player.role == PLAYER_ROLE_HUMAN:
                humans_alive += 1
            if player.role == PLAYER_ROLE_INFECTED:
                infeteds_alive += 1
            if player.role == PLAYER_ROLE_THE_THING:
                the_thing_is_alive = True

        if not the_thing_is_alive:
            msg = WS_STATUS_HUMANS_WIN
        elif the_thing_is_alive and infeteds_alive ==  match.number_players -1:
            msg = WS_STATUS_THE_THING_WIN
        elif the_thing_is_alive and humans_alive == 0:
            msg = WS_STATUS_INFECTEDS_WIN
        else:
            msg = MATCH_CONTINUES
        return msg
    
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

def set_winners(match_id, result):
    """
    Set the winners for the diferent results

    Args:
        match_id (int)
    
    Returns:
        None
    """
    with db_session:
        match = MatchDB.get(id=match_id)
        players = select(p for p in match.players)[:]
        
        for player in players:
            if result == WS_STATUS_HUMANS_WIN and player.role == PLAYER_ROLE_HUMAN :
                player.winner = True
            elif result == WS_STATUS_THE_THING_WIN and player.role == PLAYER_ROLE_THE_THING:
                player.winner = True
            elif result == WS_STATUS_INFECTEDS_WIN and player.role == PLAYER_ROLE_INFECTED or player.role == PLAYER_ROLE_THE_THING:
                player.winner = True
            else:
                player.winner = False
        flush()

def declare_end(match_id):
    status = check_match_end(match_id)
    end_match(match_id)
    
    if status == WS_STATUS_THE_THING_WIN or status == WS_STATUS_INFECTEDS_WIN:
        set_winners(match_id,status)
    else:
        status = WS_STATUS_HUMANS_WIN

    return status

MATCHES: List[Match] = []
