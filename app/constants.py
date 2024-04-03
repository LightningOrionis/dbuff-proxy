from enum import Enum
from typing import Any, List


class ListedEnum(Enum):
    """Listed enum that inherits enum.Enum but implements list method to get all possible values."""

    @classmethod
    def list(cls) -> List[Any]:  # noqa
        """Return list of possible enum values."""
        return [c.value for c in cls]


class LobbyType(ListedEnum):
    """Enum with all possible lobby types."""

    RANKED = "Ranked"
    NORMAL = "Normal"
    TOURNAMENT = "Tournament"
    BATTLE_CUP = "Battle Cup"
    UNKNOWN = "Unknown"
    BOT = "Bot"


class GameMode(ListedEnum):
    """Enum with all possible game modes."""

    ALL_PICK = "All Pick"
    TURBO = "Turbo"
    MUTATION = "Mutation"
    CAPTAINS_MODE = "Captains Mode"
    RANDOM_DRAFT = "Random Draft"
    SINGLE_DRAFT = "Single Draft"

    SOLO_MID = "1v1 Solo Mid"
    ABILITY_DRAFT = "Ability Draft"
    ALL_RANDOM = "All Random"
    DEATH_MATCH = "All Random Deathmatch"
    LEAST_PLAYED = "Least Played"
    LIMITED_HERO_POOL = "Limited Hero Pool"

    CUSTOM_GAME = "Custom Game"


class Team(ListedEnum):
    """Enum with possible teams."""

    RADIANT = "Radiant"
    DIRE = "Dire"


class GameResult(ListedEnum):
    """Enum with possible game results."""

    WON = "Won"
    LOST = "Lost"
    ABANDONED = "Abandoned"


ALLOWED_MATCH_AGGREGATION_KEYS = [*Team.list(), *LobbyType.list(), *GameMode.list(), "Other"]
