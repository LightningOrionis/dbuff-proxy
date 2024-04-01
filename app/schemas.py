from datetime import time, datetime
from typing import List, Dict

from pydantic import BaseModel

from app.constants import LobbyType, GameMode, Team, GameResult


class MatchInfo(BaseModel):
    duration: time
    timestamp: datetime
    lobby_type: LobbyType
    game_mode: GameMode


class BaseMatchHero(BaseModel):
    hero_name: str
    kills: int
    deaths: int
    assists: int


class AdvancedMatchHero(BaseMatchHero):
    """Player in match"""
    player_id: int
    net_worth: int
    gpm: int
    xpm: int
    hero_damage: int
    tower_damage: int
    heal: int
    last_hits: int
    denies: int


class PlayerMatch(BaseModel):
    """PlayerMatch model."""
    result: GameResult
    hero: BaseMatchHero
    match_info: MatchInfo


class Match(BaseModel):
    """Match model."""
    winner: Team
    players: Dict[Team, List[AdvancedMatchHero]]
    match_info: MatchInfo


class PlayerProfile(BaseModel):
    """PlayerProfile model."""


class Record(BaseModel):
    """Record model."""
    match_info: MatchInfo
    result: GameResult
    record_name: str
    hero_name: str
    value: str
