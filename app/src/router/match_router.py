import json

from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect, HTTPException

from app.src.game.player import *
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
    live_match = get_live_match_by_id(input.match_id)
    match_db = get_match_by_id(input.match_id)

    # check if match exists and if it is not finalized
    if live_match == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )

    # check if match is started
    if match_db.started:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match already started",
        )

    # check if match is full
    if match_db.number_players >= match_db.max_players:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Match is full",
        )

    match_out = await join_match(input.player_name, input.match_id)

    return JoinMatchOut(
        player_id=match_out["player_id"], match_name=match_out["match_name"]
    )


@router.get(
    "/matches/{match_id}/players/{player_id}/get_card",
    response_model=CardModel,
    status_code=status.HTTP_200_OK
)
@db_session
async def get_card_endpoint(match_id: int, player_id: int):
    """
    try:
        match = MatchDB.get(id=match_id)
        player = PlayerDB.get(id=player_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )
    if match == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )
    elif player == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )
    elif  not match.started:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED ,
            detail="Match has not started",
        )
    """
    """card = get_card(match_id,player_id)
    return CardModel(
        card_id= card["card_id"],
        name= card["name"],
        image= card["card_image"]
        )
    """
    return CardModel(card_id=3,name= "sadda", image="asdasd")

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
