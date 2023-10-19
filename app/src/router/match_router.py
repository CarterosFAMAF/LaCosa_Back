import json

from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect, HTTPException
import random
from app.src.game.player import *
from app.src.game.match import *
from app.src.game.constants import *
from app.src.game.card import *

from app.src.websocket.constants import *
from app.src.websocket.match_connection_manager import *

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

    match_out = join_match(input.player_name, input.match_id)

    # send message to all players in the match
    ws_msg = create_ws_message(
        input.match_id, WS_STATUS_PLAYER_JOINED, match_out["player_id"]
    )
    match = get_live_match_by_id(input.match_id)
    await match._match_connection_manager.broadcast_json(ws_msg)

    return JoinMatchOut(
        player_id=match_out["player_id"], match_name=match_out["match_name"]
    )


@router.put(
    "/matches/{match_id}/players/{player_in_id}/{player_out_id}/{card_id}/play_card",
    status_code=status.HTTP_200_OK,
)
async def play_card_endpoint(match_id, player_in_id, player_out_id, card_id):
    # convert all the fields to int
    match_id = int(match_id)
    player_in_id = int(player_in_id)
    player_out_id = int(player_out_id)
    card_id = int(card_id)
    
    # check if match exists and if it is not finalized
    match = get_match_by_id(match_id)
    if match == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )
    elif match.started == False:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Match has not started",
        )

    # check if player in exists
    player_in = get_player_by_id(player_in_id)
    if player_in == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    # check if player out exists
    player_out = None
    if player_out_id != 0:
        player_out = get_player_by_id(player_out_id)
        if player_out == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found",
            )
            
    card = get_card_by_id(card_id)
    if card == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
    status = play_card(player_in, player_out, match_id, card_id)
    
    # send lanzallamas message to all players
    live_match = get_live_match_by_id(match_id)
    print(live_match)
    msg_ws = create_ws_message(match_id, status, player_in_id, player_out_id)
    await live_match._match_connection_manager.broadcast_json(msg_ws)

    next_turn(match_id)

    # send next turn message to all players in the match
    ws_msg = create_ws_message(match_id, WS_STATUS_NEW_TURN, player_in_id)
    live_match = get_live_match_by_id(match_id)
    live_match._match_connection_manager.broadcast_json(ws_msg)

    return {"message": "Card played"}

@router.put(
    "/matches/{match_id}/players/{player_id}/{card_id}/discard",
)
async def discard(match_id,player_id,card_id):

    match = get_match_by_id(match_id)
    if match == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )
    elif match.started == False:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Match has not started",
        )

    # check if player in exists
    player = get_player_by_id(player_id)
    if player== None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )
    
    card = get_card_by_id(card_id)
    if card == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found",
        )
        
    discard_card_of_player(card_id, match_id, player_id)
    
    next_turn(match_id)
    
    live_match = get_live_match_by_id(match.id)
    print(live_match)
    msg_ws = create_ws_message(match.id, WS_STATUS_DISCARD , player.id)
    await live_match._match_connection_manager.broadcast_json(msg_ws)
    return {"message" : "Card discard"}



@router.get(
    "/matches/{match_id}/players/{player_id}/get_card",
    response_model=CardModel,
    status_code=status.HTTP_200_OK,
)
async def get_card_endpoint(match_id: int, player_id: int):
    with db_session:
        match = MatchDB.get(id=match_id)
        player = PlayerDB.get(id=player_id)
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
        elif not match.started:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Match has not started",
            )
    card = get_card(match_id, player_id)
    return CardModel(id=card["id"], name=card["name"], image=card["image"])


@router.get(
    "/matches/{match_id}/players/{player_id}/get_hand", status_code=status.HTTP_200_OK
)
async def get_hand(match_id: int, player_id: int):
    with db_session:
        match = MatchDB.get(id=match_id)
        player = PlayerDB.get(id=player_id)
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
        elif not match.started:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Match has not started",
            )
    hand = get_player_hand(match_id, player_id)
    return hand


@router.put("/matches/{match_id}/start_game", status_code=status.HTTP_200_OK)
async def start_match(input: StartMatchIn):
    with db_session:
        match = MatchDB.get(id=input.match_id)
        player = PlayerDB.get(id=input.player_id)
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
        elif player.id != match.player_owner.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner can start the match",
            )
        elif match.number_players < match.min_players:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="There are not enough players",
            )

    start_game(input.match_id)

    ws_msg = create_ws_message(match.id, WS_STATUS_MATCH_STARTED)

    match = get_live_match_by_id(match.id)
    await match._match_connection_manager.broadcast_json(ws_msg)

    msg = {"message": "The match has been started"}
    return msg

@router.put(
    "/matches/{match_id}/players/{player_in_id}/{player_out_id}/{card_id}/play_card_investigation",
    status_code=status.HTTP_200_OK,
)
async def play_card_investigation_endpoint(match_id,player_id,player_target_id,card_id):
    with db_session:
        match = get_match_by_id(match_id)
        if match == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found",
            )
        elif match.started == False:
            raise HTTPException(
                status_code=status.HTTP_412_PRECONDITION_FAILED,
                detail="Match has not started",
            )

        # check if player in exists
        player = get_player_by_id(player_id)
        if player== None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found",
            )
        
        card = get_card_by_id(card_id)
        if card == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found",
            )
            
        match_live = get_live_match_by_id(match.id)
        print(match_live)
        player_target = get_player_by_id(player_target_id)
            
        card_random = play_card_investigation(player_target,card)
        
        #al player deberia mandarle que carto tiene el jugador objetivo
        msg_ws = create_ws_message(match.id,WS_STATUS_CARD_DISCOVER,player.id,player_target.id,card_random["name"])
        await match_live._match_connection_manager.send_personal_json(msg_ws,player_id)
        
        #al player afectado por la carta le manda un msj de que han visto su carta y cual
        msg_ws = create_ws_message(match.id,WS_STATUS_CARD_SHOWN,player.id,player_target.id,card_random["name"]) 
        await match_live._match_connection_manager.send_personal_json(msg_ws,player_target.id)
        
        #por ahora se jugo una carta sospecha.
        msg_ws = create_ws_message(match.id,WS_STATUS_SUSPECT,player.id,player_target.id)
        await match_live._match_connection_manager.broadcast_json(msg_ws)
        
        discard_card_of_player(card.id,match.id,player.id)
        
        return CardModel(id=card_random["id"], name=card_random["name"], image=card_random["image"])
    


@router.websocket("/ws/matches/{match_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int, player_id: int):
    try:
        player = get_player_by_id(player_id)
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
        await manager.disconnect(websocket, player_id, match._id)
        remove_player_from_match(player_id, match._id)
        print(f"Player {player.name} disconnected from match {match._id}")
