import json

from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect

from app.src.game.player import Player
from app.src.game.match import Match, MATCHES
from app.src.models.schemas import MatchIn, MatchOut, JoinMatchOut


router = APIRouter()


@router.post("/matches", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchIn):
    new_match = Match(
        match.player_name,
        match.match_name,
        match.max_players,
        match.min_players,
    )

    return MatchOut(
        match_id=new_match._id,
        owner_id=new_match._player_owner_id,
        match_name=match.match_name,
        result="Match created",
    )


@router.post("/matches/{match_id}/join")
async def join_match_endpoint(player_name: str, match_id: int):
    # necesito traer la clase match.
    match_out = Match.join_match(player_name, match_id)

    return JoinMatchOut(
        player_id=match_out["player_id"], match_name=match_out["match_name"]
    )


# websocket endpoint


@router.websocket("/ws/matches/{match_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int, player_id: int):
    # TODO: move validation to a function in schemas.py?

    try:
        player = Player.get_player_by_id(player_id)
    except:
        raise "Player not found"
    if player == None:
        raise "Player not found"

    try:
        lobby_id = Match.get_match_lobby_id(match_id)
    except:
        raise "Match not found"
    if lobby_id == None:
        raise "Match not found"

    match = MATCHES[lobby_id]

    manager = match._match_connection_manager

    await manager.connect(websocket, player_id)

    try:
        while True:
            msg = await websocket.receive_text()

    except WebSocketDisconnect:
        await manager.disconnect(websocket)

        await manager.broadcast_json(1, "Alguno abandono la partida", {})
