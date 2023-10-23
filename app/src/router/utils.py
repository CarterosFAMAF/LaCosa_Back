from app.src.websocket.constants import *
from app.src.websocket.match_connection_manager import create_ws_message
from app.src.game.match import get_live_match_by_id


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
    match = get_live_match_by_id(match_id)

    if (
        status == WS_STATUS_PLAYER_BURNED
        or status == WS_STATUS_CHANGED_OF_PLACES
        or status == WS_STATUS_REVERSE_POSITION
        or status == WS_STATUS_ANALISIS
    ):
        ws_msg = create_ws_message(
            match_id=match_id,
            status=status,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name="",
            list_revealed_card=[],
        )
        await match._match_connection_manager.broadcast_json(ws_msg)

    elif status == WS_STATUS_WHISKY:
        ws_msg = create_ws_message(
            match_id=match_id,
            status=status,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name="",
            list_revealed_card=list_cards,
        )
        await match._match_connection_manager.broadcast_json(ws_msg)

    elif status == WS_STATUS_SOSPECHA:
        # send private msg to notice card seen
        msg_ws = create_ws_message(
            match_id=match_id,
            status=WS_STATUS_CARD_SHOWN,
            player_id=player_in_id,
            player_target_id=player_out_id,
            list_revealed_card=list_card[0]["name"],
        )
        await send_personal_message(player_out_id, msg_ws)

        # send public msg
        msg_ws = create_ws_message(
            match_id=match_id,
            status=status,
            player_id=player_in_id,
            player_target_id=player_out_id,
            card_name="",
            list_revealed_card=[],
        )
        await match._match_connection_manager.broadcast_json(msg_ws)
