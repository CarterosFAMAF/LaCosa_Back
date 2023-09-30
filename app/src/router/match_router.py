from fastapi import APIRouter, status

from app.src.game.match import Match, MATCHS
from app.src.router.schemas import MatchIn, MatchOut , JoinMatchOut
from app.src.game.match import Match

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
        result="Match created",
    )

@router.post("/matches/{match_id}/join")
async def join_match_endpoint(player_name: str,match_id : int):
    #necesito traer la clase match.
    match_out = Match.join_match(player_name,match_id)

    return JoinMatchOut ( 
        player_id = match_out["player_id"],
        match_name = match_out["match_name"] )

# websocket endpoint
"""
@router.websocket("/ws/matchs/{match_id}/{player_id}")
async def websocket_endpoint(websocket: WebSocket, match_id: int, player_id: int):
    # seteo variables para usar aca
    match = MATCHS[match_id]
    player = match._players[player_id]
    manager = match.match_connection_manager

    # seteo websocket en el objeto jugador para a futuro poder mandarle algo privado
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

"""
