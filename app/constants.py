from enum import Enum


class LobbyType(Enum):
    RANKED = "Ranked"
    NORMAL = "Normal"
    TOURNAMENT = "Tourna"  # TODO: Add tournament
    UNKNOWN = "Unknow"  # TODO: Add Unknown
    BOT = "Bot"


class GameMode(Enum):
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


class Team(Enum):
    RADIANT = "Radiant"
    DIRE = "Dire"


class GameResult(Enum):
    WON = "Won"
    LOST = "Lost"
    ABANDONED = "Abandoned"
