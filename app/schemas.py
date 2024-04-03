from datetime import datetime, time
from typing import Dict, List

from pydantic import BaseModel, field_validator

from app.constants import (
    ALLOWED_MATCH_AGGREGATION_KEYS,
    GameMode,
    GameResult,
    LobbyType,
    Team,
)


class AggregatedMatchStats(BaseModel):
    """Aggregated match statistics model."""

    winrate: float
    matches_played: int
    avg_kda: float | None = None


# Hero models
class Hero(BaseModel):
    """Hero model used for inheritance."""

    hero_name: str


class BaseMatchHero(Hero):
    """Base hero model - used in match list."""

    kills: int
    deaths: int
    assists: int


class AdvancedMatchHero(BaseMatchHero):
    """Advanced hero model - used in match details."""

    player_id: int
    net_worth: int
    gpm: int
    xpm: int
    hero_damage: int
    tower_damage: int
    heal: int
    last_hits: int
    denies: int


class OverviewHero(Hero):
    """Overview hero model - used on profile."""

    match_stats: AggregatedMatchStats


class MatchInfo(BaseModel):
    """Match info model."""

    duration: time
    timestamp: datetime
    lobby_type: LobbyType
    game_mode: GameMode


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

    player_id: int
    nickname: str
    most_played_heroes: List[OverviewHero]
    match_stats: Dict[str, AggregatedMatchStats]

    @classmethod
    @field_validator("most_played_heroes")
    def validate_most_played_heroes(cls, v: List[OverviewHero]) -> List[OverviewHero]:
        """Validate most_played_hero field to contain up to 10 items."""
        if len(v) > 10:
            raise ValueError("Most played heroes should be 10 heroes max")

        return v

    @classmethod
    @field_validator("match_stats")
    def validate_match_stats(cls, v: Dict[str, AggregatedMatchStats]) -> Dict[str, AggregatedMatchStats]:
        """Validate match_stats field to contain only restricted values as key."""
        for key in v:
            if key not in ALLOWED_MATCH_AGGREGATION_KEYS:
                raise ValueError(f"{key} is not allowed as match aggregation key.")

        return v


class Record(BaseModel):
    """Record model."""

    match_info: MatchInfo
    result: GameResult
    record_name: str
    hero_name: str
    value: str
