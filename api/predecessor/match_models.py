"""Match data models for Predecessor API."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TeamSide(Enum):
    """The two team sides in a Predecessor match."""
    DAWN = "Dawn"
    DUSK = "Dusk"


class GameMode(Enum):
    """Supported game modes."""
    RANKED = "Ranked"
    STANDARD = "Standard"
    CUSTOM = "Custom"
    PRACTICE = "Practice"
    SOLO = "Solo"
    ARENA = "Arena"
    RUSH = "Rush"
    ARAM = "ARAM"


class Region(Enum):
    """Server regions."""
    EUROPE = "Europe"
    NA_EAST = "NA East"
    NA_WEST = "NA West"
    NA = "North America"
    ASIA = "Asia"
    OCE = "Oceania"
    SEA = "Southeast Asia"
    MENA = "Middle East"
    SA = "South America"


class Role(Enum):
    """Player roles in a match."""
    NONE = "none"
    CARRY = "carry"
    OFFLANE = "offlane"
    MIDLANE = "midlane"
    SUPPORT = "support"
    JUNGLE = "jungle"
    FILL = "fill"


@dataclass(frozen=True)
class MatchPlayerData:
    """
    Data for a single player in a match.

    Attributes:
        player_name: The player's display name.
        player_uuid: The player's UUID for profile URL construction.
        hero_name: Display name of the hero played.
        hero_icon_url: URL to the hero's icon image.
        team: Which team the player was on (Dawn/Dusk).
        role: The player's role in the match (carry, support, etc.).
        kills: Number of kills.
        deaths: Number of deaths.
        assists: Number of assists.
        minions_killed: Total minions killed (creep score).
        gold: Total gold earned.
        mmr_change: Change in MMR (positive or negative). None if unranked.
        performance_score: Optional performance score metric. None if unavailable.
        is_opted_in: Whether this player has opted into detailed stat display.
    """
    player_name: str
    player_uuid: str
    hero_name: str
    hero_icon_url: str
    team: TeamSide
    role: Role
    kills: int
    deaths: int
    assists: int
    minions_killed: int
    gold: int
    mmr_change: int | None = None
    performance_score: float | None = None
    is_opted_in: bool = False
    
    @property
    def player_profile_url(self) -> str:
        """Get the pred.gg profile URL for this player."""
        return f"https://pred.gg/players/{self.player_uuid}"
    
    @property
    def kda_string(self) -> str:
        """Get formatted KDA string (e.g., '14/4/4')."""
        return f"{self.kills}/{self.deaths}/{self.assists}"
    
    @property
    def mmr_change_string(self) -> str | None:
        """Get formatted MMR change string (e.g., '+29' or '-15')."""
        if self.mmr_change is None:
            return None
        sign = "+" if self.mmr_change >= 0 else ""
        return f"{sign}{self.mmr_change}"


@dataclass(frozen=True)
class MatchData:
    """
    Complete match data from the Predecessor API.
    
    Attributes:
        match_uuid: The match UUID for URL construction.
        match_id: Internal match ID (may be same as UUID).
        duration_seconds: Match duration in seconds.
        game_mode: The game mode played.
        region: Server region the match was played on.
        winning_team: Which team won the match.
        dawn_score: Total kills for Dawn team.
        dusk_score: Total kills for Dusk team.
        end_time: When the match ended.
        players: List of all 10 players in the match.
    """
    match_uuid: str
    match_id: str
    duration_seconds: int
    game_mode: GameMode
    region: Region
    winning_team: TeamSide
    dawn_score: int
    dusk_score: int
    end_time: datetime
    players: tuple[MatchPlayerData, ...]
    
    @property
    def match_url(self) -> str:
        """Get the pred.gg match details URL."""
        # UUID without dashes for match URLs
        uuid_no_dashes = self.match_uuid.replace("-", "")
        return f"https://pred.gg/matches/{uuid_no_dashes}"
    
    @property
    def duration_minutes(self) -> int:
        """Get match duration in minutes (rounded)."""
        return round(self.duration_seconds / 60)
    
    @property
    def score_string(self) -> str:
        """Get formatted score string (e.g., 'Dusk (39) vs Dawn (35)')."""
        return f"Dusk ({self.dusk_score}) vs Dawn ({self.dawn_score})"
    
    @property
    def dawn_players(self) -> list[MatchPlayerData]:
        """Get all players on the Dawn team."""
        return [p for p in self.players if p.team == TeamSide.DAWN]
    
    @property
    def dusk_players(self) -> list[MatchPlayerData]:
        """Get all players on the Dusk team."""
        return [p for p in self.players if p.team == TeamSide.DUSK]
    
    @property
    def opted_in_players(self) -> list[MatchPlayerData]:
        """Get only players who have opted into detailed display."""
        return [p for p in self.players if p.is_opted_in]
    
    @property
    def winning_players(self) -> list[MatchPlayerData]:
        """Get all players on the winning team."""
        if self.winning_team == TeamSide.DAWN:
            return self.dawn_players
        return self.dusk_players
    
    @property
    def losing_players(self) -> list[MatchPlayerData]:
        """Get all players on the losing team."""
        if self.winning_team == TeamSide.DAWN:
            return self.dusk_players
        return self.dawn_players




