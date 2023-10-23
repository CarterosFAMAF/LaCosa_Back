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

from app.src.router.utils import *


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
    if live_match == None or match_db == None:
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
    response_model=List[CardModel],
    status_code=status.HTTP_200_OK,
)
async def play_card_endpoint(match_id, player_in_id, player_out_id, card_id):
    # convert all the fields to int
    match_id = int(match_id)
    player_in_id = int(player_in_id)
    player_out_id = int(player_out_id)
    card_id = int(card_id)

    # check if match exists and if it is not finalized
    match, player_in, player_out, card, card_target = validate_match_players_and_cards(
        match_id, player_in_id, player_out_id, card_id, 0
    )

    live_match = get_live_match_by_id(match.id)
    list_card = []

    if is_investigation_card(card):
        # sospecha, whiskey, analisis
        list_card = play_card_investigation(player_in, player_out, card)
        status = create_status_investigation(card)
    else:
        status = play_card(player_in, player_out, match_id, card_id)

    # CARD PLAYED MSG
    await send_message_card_played(
        match_id=match.id,
        status=status,
        player_in_id=player_in.id,
        player_out_id=player_out.id if player_out else 0,
        card_name=card.name,
        list_cards=list_card,
    )

    discard_card_of_player(card.id, match.id, player_in.id)
    ws_msg = create_ws_message(match_id, WS_STATUS_DISCARD, player_in_id)
    await live_match._match_connection_manager.broadcast_json(ws_msg)

    # NEXT TURN MSG
    next_turn(match.id)
    ws_msg = create_ws_message(match_id, WS_STATUS_NEW_TURN, player_in_id)
    await live_match._match_connection_manager.broadcast_json(ws_msg)

    # FINALIZE MATCH MSG
    if check_match_end(match_id):
        end_match(match_id)
        ws_msg = create_ws_message(match_id, WS_STATUS_MATCH_ENDED)
        await live_match._match_connection_manager.broadcast_json(ws_msg)

    return list_card


@router.put(
    "/matches/{match_id}/players/{player_id}/{card_id}/discard",
)
async def discard(match_id, player_id, card_id):
    match, player, player_target, card, card_target = validate_match_players_and_cards(
        match_id, player_id, 0, card_id, 0
    )

    live_match = get_live_match_by_id(match.id)

    discard_card_of_player(card_id, match_id, player_id)
    msg_ws = create_ws_message(match.id, WS_STATUS_DISCARD, player.id)
    await live_match._match_connection_manager.broadcast_json(msg_ws)

    next_turn(match_id)
    ws_msg = create_ws_message(match_id, WS_STATUS_NEW_TURN, player.id)
    await live_match._match_connection_manager.broadcast_json(ws_msg)

    return {"message": "Card discard"}


@router.get(
    "/matches/{match_id}/players/{player_id}/get_card",
    response_model=CardModel,
    status_code=status.HTTP_200_OK,
)
async def get_card_endpoint(match_id: int, player_id: int):
    match, player, player_target, card, card_target = validate_match_players_and_cards(
        match_id, player_id, 0, 0, 0
    )

    card = get_card(match_id, player_id)
    return CardModel(id=card["id"], name=card["name"], image=card["image"])


@router.get(
    "/matches/{match_id}/players/{player_id}/get_hand", status_code=status.HTTP_200_OK
)
async def get_hand(match_id: int, player_id: int):
    match, player, player_target, card, card_target = validate_match_players_and_cards(
        match_id, player_id, 0, 0, 0
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

        # if the match has ended

        if (
            (match_db != None)
            and (match_db.started == True)
            and (match_db.finalized == False)
        ):
            await manager.disconnect(websocket, player_id, match._id)
            end_match(match_id)
            print("if the match has started end match.")
            ws_msg = create_ws_message(match_id, WS_STATUS_MATCH_ENDED)
            await manager.broadcast_json(ws_msg)

        # if the match has not started and host disconnects, delete match.
        elif (
            match_db != None
            and player_id == match_db.player_owner.id
            and (match_db.finalized == False)
        ):
            await manager.disconnect(websocket, player_id, match._id)

            print("if the match has not started and host disconnects, delete match.")
            ws_msg = create_ws_message(match_id, WS_STATUS_MATCH_ENDED)
            await manager.broadcast_json(ws_msg)

            delete_live_match(match_id)
            delete_match(match_id)

        # if the match has not started and player disconnects, delete player.
        elif match_db != None and match_db.finalized == False:
            print("if the match has not started and player disconnects, delete player")
            delete_player(player_id, match_id)
            await manager.disconnect(websocket, player_id, match._id)

        else:
            await manager.disconnect(websocket, player_id, match_id)

        print(f"Player {player.name} disconnected from match {match._id}")
