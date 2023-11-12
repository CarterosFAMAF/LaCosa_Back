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
async def play_card_endpoint(match_id: int, player_in_id, player_out_id, card_id):
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

    can_defend_bool, list_card = can_defend(player_out_id, card.card_id)
    if can_defend_bool:  # si el target tiene nada de barbacoas
        # deberia mandarle el id de la carta del jugador main.
        await send_message_private_defense(
            match_id=match.id,
            player_in_id=player_in.id,
            card_id=card.id,
            player_out_id=player_out.id if player_out else 0,
            card_name=card.name,
            list_card=list_card,
        )
        return []

    elif is_investigation_card(card):  # sospecha, whiskey, analisis
        list_card = play_card_investigation(player_in, player_out, card,match)
        status = create_status_investigation(card)
        discard_card_of_player(card.id, match.id, player_in.id)

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
    if card.card_id == WHISKY or card.card_id == QUE_QUEDE_ENTRE_NOSOTROS or card.card_id == UPS:
        list_card = []
    
    # DISCARD MSG
    await discard_message(match_id, player_in_id)

    return list_card



@router.put(
    "/matches/{match_id}/players/{player_id}/play_card_defense",
    response_model=List[CardModel],
    status_code=status.HTTP_200_OK,
)
async def play_card_defense_endpoint(input: PlayCardDefenseIn):
    # check if card exists
    player_main = get_player_by_id(input.player_main_id)
    player_target = get_player_by_id(input.player_target_id)
    match = get_match_by_id(input.match_id)

    if input.card_main_id != 0:
        card_main = get_card_by_id(input.card_main_id)
        if card_main == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found",
            )

    if input.card_target_id != 0:
        card_target = get_card_by_id(input.card_target_id)
        if card_target == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found",
            )
    live_match = get_live_match_by_id(input.match_id)
    list_card = []
    #caso en el que decide no defenderse
    if input.card_main_id == 0:
        # Como no hay defensa para cartas de "investigacion" nunca devolveremos una lista en play_card.

        status = play_card(
            player_target,
            player_main,
            input.match_id,
            input.card_target_id,
        )

        await send_message_card_played(
            match_id=input.match_id,
            status=status,
            player_in_id=input.player_target_id,
            player_out_id=input.player_main_id,
            card_name=card_target.name,
            list_cards=[],
        )

    #caso de fallaste , se realiza un intercambio con otro objetivo. 
    # se tiene que hacer un intercambio con is_you_failed = True

    elif card_main.card_id == FALLASTE:
        # broadcastear que el jugador se defendio con una fallaste
        new_exchange_player = get_next_player_by_player_turn(input.match_id,input.player_main_id)
        ws_msg = create_ws_message_fallaste(player_main_id=input.player_target_id, player_fallaste_id=input.player_main_id, player_target_id=new_exchange_player.id)
        await live_match._match_connection_manager.broadcast_json(ws_msg)

    else:
        status, list_card = play_card_defense(
            input.player_main_id,
            input.player_target_id,
            input.card_main_id,
            input.match_id,
        )

         # DEFENSE MSG
        await send_message_play_defense(
            match_id=input.match_id,
            status=status,
            player_in_id=input.player_main_id,
            player_out_id=input.player_target_id,
            card_name=card_main.name,
        )

        if card_main.card_id == NO_GRACIAS or card_main.card_id == ATERRADOR:
            ws_msg = create_card_exchange_message(list_card[0]["id"])
            await live_match._match_connection_manager.send_personal_json(
                ws_msg, player_target.id
            )
            if card_main.card_id == NO_GRACIAS:
                list_card = []

            player_turn = get_next_player(match)
            next_turn(input.match_id)
            ws_msg = create_ws_message(
                input.match_id, WS_STATUS_NEW_TURN, player_turn.id
            )
            await live_match._match_connection_manager.broadcast_json(ws_msg)
            
        else:
            # DISCARD's
            discard_card_of_player(input.card_target_id,input.match_id,input.player_target_id)
            await discard_message(input.match_id, input.player_target_id)
            await discard_message(input.match_id, input.player_main_id)

    return list_card


@router.put(
    "/matches/{match_id}/players/{player_id}/{card_id}/discard",
)
async def discard(match_id: int, player_id: int, card_id: int):
    match, player, player_target, card, card_target = validate_match_players_and_cards(
        match_id, player_id, 0, card_id, 0
    )

    if player.quarantine > 0:
        live_match = get_live_match_by_id(match_id)
        ws_msg = create_ws_message(match_id, WS_STATUS_DISCARD_QUARANTINE, player_id, 0, card.name)
        await live_match._match_connection_manager.broadcast_json(ws_msg)
    else:
        await discard_message(match.id, player.id)
    discard_card_of_player(card.id, match.id, player.id)

    return {"message": "Card discard"}


@router.get(
    "/matches/{match_id}/players/{player_id}/{panic}/get_card",
    response_model=CardModel,
    status_code=status.HTTP_200_OK,
)
async def get_card_endpoint(match_id,player_id,panic):
    match, player, player_target, card, card_target = validate_match_players_and_cards(
        match_id, player_id, 0, 0, 0
    )
    card = get_card(match_id,player_id,panic)
    
    if player.quarantine > 0:
        live_match = get_live_match_by_id(match_id)
        ws_msg = create_ws_message(match_id, WS_STATUS_DRAW, player_id, 0, card["name"])
        await live_match._match_connection_manager.broadcast_json(ws_msg)

    return CardModel(
        id=card["id"], name=card["name"], image=card["image"], type=card["type"]
    )


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


@router.put("/matches/{match_id}/players/revelations")
async def revelations_endpoint(input: revelationsIn):
    live_match = get_live_match_by_id(input.match_id)
    hand = get_hand(input.match_id,input.player_id)
    
    exist_infections,infected_card_id = exist_infection(hand)
    
    if exist_infections:
        ws_msg = create_card_exchange_message(infected_card_id)
        live_match._match_connection_manager.broadcast_json(ws_msg)
        
    elif input.show:    
        ws_msg = create_ws_message(input.match_id,WS_STATUS_YES,input.player_id,0,"",hand)
        live_match._match_connection_manager.broadcast_json(ws_msg)
    else:
        ws_msg = create_ws_message(input.match_id,WS_STATUS_NOPE,input.player_id)
        live_match._match_connection_manager.broadcast_json(ws_msg)
        
    return {"msg" : "revelations"}

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
    match_live = get_live_match_by_id(input.match_id)

    match = get_match_by_id(input.match_id)
    player_turn = get_player_in_turn(input.match_id)

    ws_msg = create_ws_message(input.match_id, WS_STATUS_MATCH_STARTED)
    await match_live._match_connection_manager.broadcast_json(ws_msg)

    ws_msg = create_ws_message(input.match_id, WS_STATUS_NEW_TURN, player_turn.id)
    await match_live._match_connection_manager.broadcast_json(ws_msg)
    
    msg = {"message": "The match has been started"}
    return msg


@router.get(
    "/matches/{match_id}/next_player",
    status_code=status.HTTP_200_OK,
)
async def next_player(match_id: int):
    with db_session:
        match = MatchDB.get(id=match_id)
        if match == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found",
            )

        next_player = get_next_player(match)

        return {"next_player_id": next_player.id}

# chat message endpoint
@router.post(
    "/matches/{match_id}/players/{player_id}/send_chat_message",
    status_code=status.HTTP_200_OK,
)
async def send_chat_message(input : SendMesaggeIn):
    with db_session:
        match = MatchDB.get(id=input.match_id)
        player = PlayerDB.get(id=input.owner_id)
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

    store_message(input.match_id, input.owner_id, input.text)

    live_match = get_live_match_by_id(input.match_id)

    ws_msg = create_ws_chat_message(player_id=input.owner_id, msg=input.text)
    await live_match._match_connection_manager.broadcast_json(ws_msg)

    return {"message": "Message sent"}


@router.put("/matches/{match_id}/players/{player_id}/exchange_cards")
async def exchange_endpoint(input: ExchangeCardIn):
    # validate match players and cards
    match, player, player_target, card, card_target = validate_match_players_and_cards(
        input.match_id, input.player_id, input.player_target_id, input.card_id, 0
    )

    match_live = get_live_match_by_id(match.id)

    if input.blind_date:
        card = get_card(match.id,player.id,False)
        send_card_extra_deck(input.player_id,input.card_id,input.match_id)
        ws_msg = create_card_exchange_message(card["id"])
        await match_live._match_connection_manager.send_personal_json(ws_msg,player.id)
        
        next_player = get_next_player(match)     
        next_turn(match.id)
        ws_msg = create_ws_message(match.id, WS_STATUS_NEW_TURN, next_player.id)
        await match_live._match_connection_manager.broadcast_json(ws_msg)
        
        
    elif is_player_main_turn(match, player):
        if input.player_target_id == 0:
            player_target = get_next_player(match)

        prepare_exchange_card(player.id, card.id)
        if player.quarantine > 0:
            ws_msg = create_ws_message(
                match.id, WS_STATUS_EXCHANGE_REQUEST_QUARANTINE, player.id, player_target.id, card.name 
            )
        else: 
            ws_msg = create_ws_message(
                match.id, WS_STATUS_EXCHANGE_REQUEST, player.id, player_target.id
            )
        await match_live._match_connection_manager.broadcast_json(ws_msg)

        can_defense_bool, list_card = can_defend(player_target.id, 0)

        if can_defense_bool:
            await send_message_private_defense(
                match_id=match.id,
                player_in_id=player.id,
                card_id=0,
                player_out_id=player_target.id if player_target else 0,
                card_name="",
                list_card=list_card,
            )

    else:
        prepare_exchange_card(player.id, card.id)
        receive_infected = receive_infected_card(input.player_target_id)
        card_main_id, card_target_id = apply_exchange(player.id, player_target.id)

        card_msg = create_card_exchange_message(card_main_id)
        await match_live._match_connection_manager.send_personal_json(
            card_msg, player_target.id
        )

        card_msg = create_card_exchange_message(card_target_id)
        await match_live._match_connection_manager.send_personal_json(
            card_msg, player.id
        )
        
        if player.quarantine > 0:
            ws_msg = create_ws_message(
                match.id, WS_STATUS_EXCHANGE_QUARANTINE, player.id, player_target.id, card.name 
            )
        else: 
            ws_msg = create_ws_message(
                match.id, WS_STATUS_EXCHANGE, player.id, player_target.id
            )
        
        await match_live._match_connection_manager.broadcast_json(ws_msg)
        if (send_infected_card(card) or receive_infected) and (not input.is_you_failed): 
            player_infected = None
            player_infector = None

            if (player.role == PLAYER_ROLE_HUMAN
            and player_target.role == PLAYER_ROLE_THE_THING):
                apply_effect_infeccion(player.id)
                player_infected = player.id
                player_infector = player_target.id

                ws_msg = create_ws_message(match.id, WS_STATUS_INFECTED,player_infector)
                await match_live._match_connection_manager.send_personal_json(
                    ws_msg, player_infected
                )
 
            elif (player.role == PLAYER_ROLE_THE_THING
            and player_target.role == PLAYER_ROLE_HUMAN):
                apply_effect_infeccion(player_target.id)
                player_infected = player_target.id
                player_infector = player.id
            
                ws_msg = create_ws_message(match.id, WS_STATUS_INFECTED,player_infector)
                await match_live._match_connection_manager.send_personal_json(
                        ws_msg, player_infected
                    )
        
        next_player = get_next_player(match)     
        next_turn(match.id)
        ws_msg = create_ws_message(match.id, WS_STATUS_NEW_TURN, next_player.id)
        await match_live._match_connection_manager.broadcast_json(ws_msg)

@router.put("/matches/{match_id}/next_turn",
    status_code=status.HTTP_200_OK,
)
async def next_turn_endpoint(match_id: int):
    with db_session:
        match = MatchDB.get(id=match_id)
        if match == None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found",
            )
    match_live = get_live_match_by_id(match.id)
    next_player = get_next_player(match)     
    next_turn(match.id)
    ws_msg = create_ws_message(match.id, WS_STATUS_NEW_TURN, next_player.id)
    await match_live._match_connection_manager.broadcast_json(ws_msg)



@router.put("/matches/{match_id}/players/{player_id}/declare_end")
async def declare_end_endpoint(input : declare_endIn):
    live_match = get_live_match_by_id(input.match_id)

    match_status = check_match_end(input.match_id)
    if  match_status == MATCH_CONTINUES:
        match_status = WS_STATUS_HUMANS_WIN
    
    set_winners(input.match_id, match_status)
    ws_msg = create_ws_message(input.match_id, match_status)
    await live_match._match_connection_manager.broadcast_json(ws_msg)
    end_match(input.match_id)

    return {"message" : "Match finalized"}



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
