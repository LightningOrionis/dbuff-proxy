from datetime import date
from typing import List

from fastapi import Depends
from fastapi.routing import APIRouter

from app.dependencies import get_client
from app.schemas import Match, PlayerMatch, PlayerProfile, Record
from app.services.client import DotabuffClient

router = APIRouter(prefix="/proxy")


@router.get("/match/{match_id}", response_model=Match)
async def get_match(match_id: int, dotabuff_client: DotabuffClient = Depends(get_client)) -> Match:
    """Get match data."""
    return await dotabuff_client.get_match(match_id)


@router.get("/player/{user_id}/records", response_model=List[Record])
async def get_player_records(user_id: int, dotabuff_client: DotabuffClient = Depends(get_client)) -> List[Record]:
    """Get match data."""
    return await dotabuff_client.get_records(user_id)


@router.get("/player/{user_id}/matches", response_model=List[PlayerMatch])
async def get_player_matches(
    user_id: int,
    dotabuff_client: DotabuffClient = Depends(get_client),
    start_date: date = None,
    end_date: date = None,
) -> List[PlayerMatch]:
    """Get match data."""
    return await dotabuff_client.get_matches(user_id, start_date, end_date)


@router.get("/player/{user_id}/profile", response_model=PlayerProfile)
async def get_player_profile(user_id: int, dotabuff_client: DotabuffClient = Depends(get_client)) -> PlayerProfile:
    """Get match data."""
    return await dotabuff_client.get_player_profile(user_id)
