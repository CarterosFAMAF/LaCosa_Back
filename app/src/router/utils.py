from app.src.websocket.constants import *
from app.src.websocket.match_connection_manager import create_ws_message
from app.src.game.match import get_live_match_by_id
from app.src.websocket.match_connection_manager import *
from app.src.game.match import *
from app.src.game.card import *
# sospecha: manda un mensaje privado, 1 carta random del player target por el endpoint
# analisis: lista de cartas del player target por el endpoint
# whiskey: broadcastear a todos lista cartas player main


async def send_message_card_played(
    match_id: int,
    status: int,
    player_in_id: int,
    player_out_id: int,
    card_name: str,
    list_cards: list,
):
    """
    Send websocket messages depending on the card played

    Args:
        match_id (int)
        status (int)
        player_in_id (int)
        player_out_id (int)
        card_name (str)
        list_cards (list)

    Returns:
        None
    """

    # Get live match
    live_match = get_live_match_by_id(match_id)
    if (
        status == WS_STATUS_PLAYER_BURNED
        or status == WS_STATUS_CHANGED_OF_PLACES
        or status == WS_STATUS_REVERSE_POSITION
        or status == WS_STATUS_ANALYSIS  # analisis no se va a mostrar nunca.
        or status == WS_STATUS_DETERMINATION
        or status == WS_STATUS_SEDUCCION
        or status == WS_STATUS_BLIND_DATE
        or status == WS_STATUS_QUARANTINE
        or status == WS_STATUS_AXE
    ):
        ws_msg = create_ws_message(
            match_id=match_id,
            status=status,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name="",
            list_revealed_card=[],
        )
        await live_match._match_connection_manager.broadcast_json(ws_msg)

    elif status == WS_STATUS_WHISKY or status == WS_STATUS_UPS:
        ws_msg = create_ws_message(
            match_id=match_id,
            status=status,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name="",
            list_revealed_card=list_cards,
        )
        await live_match._match_connection_manager.broadcast_json(ws_msg)

    elif status == WS_STATUS_LET_IT_REMAIN_BETWEEN_US:
        ws_msg = create_ws_message(
            match_id=match_id,
            status=status,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name="",
            list_revealed_card=list_cards,
        )
        await live_match._match_connection_manager.broadcast_json(ws_msg)

        """ 
        ws_msg = create_ws_message(
            match_id=match_id,
            status=WS_STATUS_SHOWS,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name="",
            list_revealed_card=list_cards,
        )
        await live_match._match_connection_manager.send_personal_json(
            ws_msg, player_out_id
        )
        """


    elif status == WS_STATUS_SUSPECT:
        # send private msg to notice card seen
        msg_ws = create_ws_message(
            match_id=match_id,
            status=WS_STATUS_CARD_SHOWN,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name=list_cards[0]["name"],
            list_revealed_card=[],
        )
        await live_match._match_connection_manager.send_personal_json(
            msg_ws, player_out_id
        )

        # send public msg
        msg_ws = create_ws_message(
            match_id=match_id,
            status=WS_STATUS_SUSPECT,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name="",
            list_revealed_card=[],
        )
        await live_match._match_connection_manager.broadcast_json(msg_ws)


async def send_message_private_defense(
    match_id: int,
    player_in_id: int,
    card_id: int,
    player_out_id: int,
    card_name: str,
    list_card: list,
):
    """
    Send defense message to a particular player

    Args:
        match_id (int)
        status (int
        player_in_id (int)
        player_out_id (int)
        card_name (str)

    Returns:
        None
    """

    # Get live match
    live_match = get_live_match_by_id(match_id)
    # necesito mandar el id del jugador que esta en turno y el id de la carta.
    msg_ws = create_msg_defense(player_in_id, card_id, card_name, list_card)

    await live_match._match_connection_manager.send_personal_json(msg_ws, player_out_id)


# send_message_play_defense = send_message_defense --> esto lo comente porque no lo entendi


async def send_message_play_defense(
    match_id, status, player_in_id, player_out_id, card_name
):
    live_match = get_live_match_by_id(match_id)

    msg_ws = create_ws_message(
        match_id=match_id,
        status=status,
        player_id=player_in_id,
        player_target_id=player_out_id,
        card_name=card_name,
        list_revealed_card=[],
    )
    await live_match._match_connection_manager.broadcast_json(msg_ws)


def validate_match_players_and_cards(
    match_id, player_in_id, player_out_id, card_id, card_target_id
):
    match = get_match_by_id(match_id)
    if match is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match not found",
        )
    elif match.started is False:
        raise HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail="Match has not started",
        )

    player_in = get_player_by_id(player_in_id)
    if player_in is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found",
        )

    player_out = None
    if player_out_id != 0:
        player_out = get_player_by_id(player_out_id)
        if player_out is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found",
            )
    card = None
    if card_id != 0:
        card = get_card_by_id(card_id)
        if card is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found",
            )
    card_target = None
    if card_target_id != 0:
        card_target = get_card_by_id(card_target_id)
        if card_target is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Card not found",
            )

    return match, player_in, player_out, card, card_target


async def discard_message(match_id, player_id):
    live_match = get_live_match_by_id(match_id)
    ws_msg = create_ws_message(match_id, WS_STATUS_DISCARD, player_id)
    await live_match._match_connection_manager.broadcast_json(ws_msg)


async def broadcast_of_card_played(player_id,card_id,match_id):
    live_match = get_live_match_by_id(match_id)
    ws_msg = create_ws_message_play_card(player_id,card_id)

    await live_match._match_connection_manager.broadcast_json(ws_msg)
