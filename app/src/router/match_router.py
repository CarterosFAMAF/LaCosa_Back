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
    response_model=CardModel,
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
    live_match = get_live_match_by_id(match_id)
    print(live_match)

    card_random = CardModel(id=0, name="", image="")

    if is_investigation_card(card):
        card_random = play_card_investigation(player_out, card)

        # al player afectado por la carta le manda un msj de que han visto su carta y cual
        msg_ws = create_ws_message(
            match.id,
            WS_STATUS_CARD_SHOWN,
            player_in.id,
            player_out.id,
            card_random["name"],
        )
        await live_match._match_connection_manager.send_personal_json(
            msg_ws, player_out.id
        )

        # status de carta sospecha
        status = WS_STATUS_SUSPECT

    else:
        status = play_card(player_in, player_out, match_id, card_id)

    # send message to all players of the card played
    msg_ws = create_ws_message(match_id, status, player_in.id, player_out_id)
    await live_match._match_connection_manager.broadcast_json(msg_ws)

    next_turn(match_id)
    # send next turn message to all players in the match
    ws_msg = create_ws_message(match_id, WS_STATUS_NEW_TURN, player_in_id)
    await live_match._match_connection_manager.broadcast_json(ws_msg)

    # check if match has ended
    if check_and_set_match_end(match_id):
        end_match(match_id)
        ws_msg = create_ws_message(match_id, WS_STATUS_MATCH_ENDED)
        await live_match._match_connection_manager.broadcast_json(ws_msg)

    # return card model , if not played card investigation return empty (traducido como pintó)
    return card_random


@router.put(
    "/matches/{match_id}/players/{player_id}/{card_id}/discard",
)
async def discard(match_id, player_id, card_id):
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
    if player == None:
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

    msg_ws = create_ws_message(match.id, WS_STATUS_DISCARD, player.id)
    await live_match._match_connection_manager.broadcast_json(msg_ws)

    return {"message": "Card discard"}


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


# endpoin to list matches
@router.get(
    "/matches", response_model=List[ListMatchOut], status_code=status.HTTP_200_OK
)
async def list_matches():
    matches = list_not_started_matches()
    return matches


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
        # if the match has started end match.
        match_db = get_match_by_id(match_id)

        if match_db != None and match_db.started == True:
            await manager.disconnect(websocket, player_id, match._id)
            end_match(match_id)
            print("if the match has started end match.")
            ws_msg = create_ws_message(match_id, WS_STATUS_MATCH_ENDED)
            await manager.broadcast_json(ws_msg)

        # if the match has not started and host disconnects, delete match.
        elif match_db != None and player_id == match_db.player_owner.id:
            await manager.disconnect(websocket, player_id, match._id)

            print("if the match has not started and host disconnects, delete match.")
            ws_msg = create_ws_message(match_id, WS_STATUS_MATCH_ENDED)
            await manager.broadcast_json(ws_msg)

            delete_match(match_id)

        # if the match has not started and player disconnects, delete player.
        elif match_db != None:
            print("if the match has not started and player disconnects, delete player")
            delete_player(player_id, match_id)
            await manager.disconnect(websocket, player_id, match._id)

        else:
            await manager.disconnect(websocket, player_id, match_id)

        print(f"Player {player.name} disconnected from match {match._id}")
