from fastapi import APIRouter, WebSocket, status

from src.game.match import Match

from schemas import MatchIn, MatchOut

router = APIRouter()


@router.post("/matchs", response_model=MatchOut, status_code=status.HTTP_201_CREATED)
async def create_match(match: MatchIn):
    new_match = Match(
        match.player_name,
        match.match_name,
        match.max_players,
        match.min_players,
    )
    return MatchOut(
        id=new_match.id,
        name=new_match.name,
        owner=new_match.owner.id,
        result="Match created",
    )
