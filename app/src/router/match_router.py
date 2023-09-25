from fastapi import APIRouter, status, HTTPException, WebSocket, WebSocketDisconnect
from app.src.game.match import Match, MATCHS

from app.src.router.schemas import MatchIn, MatchOut


router = APIRouter()


@router.post("/matchs", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchIn):
    try:
        new_match = Match(
            match.player_name,
            match.match_name,
            match.max_players,
            match.min_players,
        )
    except ValueError as e:
        raise HTTPException(
            {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "detail": str(e),
            }
        )
    return MatchOut(
        match_id=new_match.id,
        match_name=new_match.name,
        owner_id=new_match.owner.id,
        result="Match created",
    )


# websocket endpoint
@router.websocket("/ws/matchs/{match_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int, player_id: int):
    # seteo variables para usar aca
    match = MATCHS[match_id]
    player = match.players[player_id]
    manager = match.match_connection_manager

    player.websocket = websocket

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{player.name} says: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast(f"Client #{player.name} left the chat")
