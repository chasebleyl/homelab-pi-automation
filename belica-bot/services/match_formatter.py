"""Discord message formatter for match data."""
import discord
from typing import Optional
from models import MatchData, MatchPlayerData, TeamSide
from .hero_emoji_mapper import HeroEmojiMapper


class MatchMessageFormatter:
    """Formats MatchData into Discord embeds and components."""
    
    # Team colors
    DUSK_COLOR = discord.Color.from_rgb(75, 83, 97)    # Dark slate
    DAWN_COLOR = discord.Color.from_rgb(255, 193, 87)  # Golden yellow
    VICTORY_COLOR = discord.Color.from_rgb(87, 187, 138)  # Green
    DEFEAT_COLOR = discord.Color.from_rgb(237, 66, 69)  # Red
    NEUTRAL_COLOR = discord.Color.from_rgb(128, 128, 128)  # Gray
    
    # Emoji for visual elements
    VICTORY_EMOJI = "🏆" # discord :trophy:
    DEFEAT_EMOJI = "☠️"  # discord :skull_crossbones:
    
    def __init__(
        self,
        match: MatchData,
        subscribed_player_uuids: set[str] | None = None,
        hero_emoji_mapper: Optional[HeroEmojiMapper] = None
    ) -> None:
        """
        Initialize the match formatter.
        
        Args:
            match: The match data to format
            subscribed_player_uuids: Set of player UUIDs that should be included
                                    even if they haven't opted in (guild-specific subscriptions)
            hero_emoji_mapper: Optional mapper for hero emojis. If provided, hero emojis will be used.
        """
        self.match = match
        self.subscribed_player_uuids = subscribed_player_uuids or set()
        self.hero_emoji_mapper = hero_emoji_mapper
    
    def _determine_embed_color(self) -> discord.Color:
        """
        Determine the embed color based on subscribed players' teams.
        
        Returns:
            VICTORY_COLOR if all subscribed players won
            DEFEAT_COLOR if all subscribed players lost
            NEUTRAL_COLOR if subscribed players are on different teams or none subscribed
        """
        if not self.subscribed_player_uuids:
            return self.NEUTRAL_COLOR
        
        # Find all subscribed players in this match
        subscribed_players = [
            p for p in self.match.players
            if p.player_uuid in self.subscribed_player_uuids
        ]
        
        if not subscribed_players:
            return self.NEUTRAL_COLOR
        
        # Check if all subscribed players are on the same team
        teams = {p.team for p in subscribed_players}
        
        if len(teams) > 1:
            # Subscribed players are on different teams
            return self.NEUTRAL_COLOR
        
        # All subscribed players are on the same team
        subscribed_team = teams.pop()
        
        # Check if that team won
        if subscribed_team == self.match.winning_team:
            return self.VICTORY_COLOR
        else:
            return self.DEFEAT_COLOR
    
    def create_embed(self) -> discord.Embed:
        """
        Create the main Discord embed for the match.
        
        Returns:
            A Discord Embed with match details and opted-in player stats.
        """
        embed = discord.Embed(
            title="Click here to view more",
            url=self.match.match_url,
            color=self._determine_embed_color(),
        )
        
        # Match overview section
        embed.description = self._build_match_overview()
        
        # Winning team section with opted-in player details
        winning_section = self._build_team_section(
            team=self.match.winning_team,
            players=self.match.winning_players,
            is_winner=True,
        )
        if winning_section:
            embed.add_field(
                name=f"{self.match.winning_team.value} - {self.VICTORY_EMOJI} Victory",
                value=winning_section,
                inline=False,
            )
        
        # Losing team section with opted-in player details
        losing_team = TeamSide.DAWN if self.match.winning_team == TeamSide.DUSK else TeamSide.DUSK
        losing_section = self._build_team_section(
            team=losing_team,
            players=self.match.losing_players,
            is_winner=False,
        )
        if losing_section:
            embed.add_field(
                name=f"{losing_team.value} - {self.DEFEAT_EMOJI} Defeat",
                value=losing_section,
                inline=False,
            )
        
        # Footer with match ID and timestamp
        embed.set_footer(text=self.match.match_uuid.replace("-", ""))
        embed.timestamp = self.match.end_time
        
        return embed
    
    def create_view(self) -> discord.ui.View:
        """
        Create the button view for the match message.
        
        Returns:
            A Discord View with action buttons.
        """
        view = discord.ui.View()
        
        # "Open" button links to match details
        open_button = discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label="Open",
            emoji="🔗",
            url=self.match.match_url,
        )
        view.add_item(open_button)
        
        return view
    
    def _build_match_overview(self) -> str:
        """Build the match overview description text."""
        lines = [
            f"**{self.match.score_string}**",
            "",
            f"**Duration:** {self.match.duration_minutes} Minutes",
            f"**Region:** {self.match.region.value}",
            f"**Gamemode:** {self.match.game_mode.value}",
        ]
        return "\n".join(lines)
    
    def _build_team_section(
        self,
        team: TeamSide,
        players: list[MatchPlayerData],
        is_winner: bool,
    ) -> str | None:
        """
        Build the player list section for a team.
        
        Includes players who have opted in OR are subscribed via guild subscriptions.
        
        Args:
            team: The team side.
            players: List of players on this team.
            is_winner: Whether this is the winning team.
            
        Returns:
            Formatted string with player details, or None if no players to display.
        """
        # Include players who are opted in OR subscribed
        included = [
            p for p in players
            if p.is_opted_in or p.player_uuid in self.subscribed_player_uuids
        ]
        
        if not included:
            return None
        
        lines = []
        for player in included:
            line = self._format_player_line(player)
            lines.append(line)
        
        return "\n".join(lines)
    
    def _format_player_line(self, player: MatchPlayerData) -> str:
        """
        Format a single player's stats line.
        
        Format: +29 [HeroName] **PlayerName** 14/4/4 159.37 PS
        
        Args:
            player: The player data to format.
            
        Returns:
            Formatted player line with markdown.
        """
        parts = []
        
        # MMR change (if available)
        if player.mmr_change_string:
            parts.append(f"`{player.mmr_change_string:>4}`")
        
        # Hero emoji or name
        if self.hero_emoji_mapper:
            hero_display = self.hero_emoji_mapper.get_emoji_or_fallback(player.hero_name)
        else:
            hero_display = f"*{player.hero_name}*"
        parts.append(hero_display)
        
        # Player name with profile link
        parts.append(f"[**{player.player_name}**]({player.player_profile_url})")
        
        # KDA
        parts.append(f"`{player.kda_string}`")
        
        # Performance score (if available)
        if player.performance_score is not None:
            parts.append(f"**{player.performance_score:.2f}** PS")
        
        return " ".join(parts)


def create_match_message(
    match: MatchData,
    subscribed_player_uuids: set[str] | None = None,
    hero_emoji_mapper: Optional[HeroEmojiMapper] = None
) -> tuple[discord.Embed, discord.ui.View]:
    """
    Convenience function to create embed and view for a match.
    
    Args:
        match: The match data to format.
        subscribed_player_uuids: Set of player UUIDs that should be included
                                even if they haven't opted in (guild-specific subscriptions)
        hero_emoji_mapper: Optional mapper for hero emojis. If provided, hero emojis will be used.
        
    Returns:
        Tuple of (embed, view) ready to send.
    """
    formatter = MatchMessageFormatter(match, subscribed_player_uuids, hero_emoji_mapper)
    return formatter.create_embed(), formatter.create_view()

