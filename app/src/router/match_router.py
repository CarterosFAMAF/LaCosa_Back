import json

from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect
from pony.orm import *
from app.src.game.player import Player
from app.src.game.match import *
from app.src.game.match_connection_manager import create_ws_message

from app.src.models.schemas import *


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


@router.post(
    "/matches/{match_id}/join",
    response_model=JoinMatchOut,
    status_code=status.HTTP_200_OK,
)
async def join_match_endpoint(input: JoinMatchIn):
    match_out = await join_match(input.player_name, input.match_id)

    return JoinMatchOut(
        player_id=match_out["player_id"], match_name=match_out["match_name"]
    )




@router.put("/matches/{match_id}/start", status_code=status.HTTP_200_OK)
@db_session
async def start_match(match_id: int, player_id:int):
    """
    try:
        player = Player.get_player_by_id(player_id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Player not found")
    try:
        match = Match.get_db_match_by_id(match_id)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Match not found")
    if player.id != match.owner.id:
        raise HTTPException(status_code=403, detail= "Only the owner can start the match")
    """
    msg = {"message": "The match has been started"}
    return msg



@router.websocket("/ws/matches/{match_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int, player_id: int):
    try:
        player = Player.get_player_by_id(player_id)
    except:
        raise ValueError("Player not found")
    if player == None:
        raise ValueError("Player not found")

    match = get_live_match_by_id(match_id)
    if match == None:
        raise ValueError("Match not found")

    manager = match._match_connection_manager

    print(f"Player {player.name} connected to match {match._id}")
    await manager.connect(websocket, player_id, match._id)
    try:
        while True:
            msg = await websocket.receive_text()

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        remove_player_from_match(player_id, match._id)
        data_ws = create_ws_message(match_id, 6, f"{player.name} se desconecto")
        await manager.broadcast_json(data_ws)
