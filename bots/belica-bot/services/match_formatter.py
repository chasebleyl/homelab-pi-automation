"""Discord message formatter for match data."""
import io
import discord
import logging
from typing import Optional
from predecessor_api import MatchData, MatchPlayerData, TeamSide, calculate_per_minute
from .hero_emoji_mapper import HeroEmojiMapper
from .role_emoji_mapper import RoleEmojiMapper

logger = logging.getLogger(__name__)


async def _handle_scoreboard_callback(interaction: discord.Interaction, match_uuid: str):
    """Shared callback logic for scoreboard button."""
    # Defer with ephemeral=True so "thinking..." is only visible to clicker
    await interaction.response.defer()

    try:
        # Access bot services via interaction.client
        bot = interaction.client

        # Check if bot has required services
        if not hasattr(bot, "match_service"):
            await interaction.followup.send(
                "Bot services not available. Please try again later.",
                ephemeral=True,
            )
            return

        # Fetch detailed match data
        match_data = await bot.match_service.fetch_detailed_match(match_uuid)
        if not match_data:
            await interaction.followup.send(
                "Could not fetch match data. The match may no longer be available.",
                ephemeral=True,
            )
            return

        # Get subscribed names for this guild (for fallback display names)
        subscribed_names: dict[str, str] = {}
        if interaction.guild_id and hasattr(bot, "profile_subscription"):
            profiles = await bot.profile_subscription.get_profiles_with_names(interaction.guild_id)
            subscribed_names = {
                p.player_uuid: p.player_name
                for p in profiles
                if p.player_name
            }

        # Import here to avoid circular imports
        from .leaderboard_image import generate_leaderboard_image

        # Generate the image
        image_bytes = generate_leaderboard_image(match_data, subscribed_names=subscribed_names)

        # Create file attachment
        filename = f"scoreboard_{match_uuid}.png"
        file = discord.File(io.BytesIO(image_bytes), filename=filename)

        # Get the original message's embed and update it to include the image
        original_embed = interaction.message.embeds[0] if interaction.message.embeds else None
        if original_embed:
            # Set the image on the embed to reference the attachment
            original_embed.set_image(url=f"attachment://{filename}")

        # Create a view with only the "Open" button (remove "View Scoreboard" since it's now shown)
        view = discord.ui.View(timeout=None)
        # Find and keep the Open button from the original message
        for component in interaction.message.components:
            for child in component.children:
                if child.url:  # URL buttons (like "Open") have a url attribute
                    view.add_item(
                        discord.ui.Button(
                            style=child.style,
                            label=child.label,
                            emoji=child.emoji,
                            url=child.url,
                        )
                    )

        # Edit the original message to include the image and remove the scoreboard button
        await interaction.message.edit(embed=original_embed, attachments=[file], view=view)

    except Exception as e:
        logger.exception(f"Error generating scoreboard for match {match_uuid}")
        await interaction.followup.send(
            f"Error generating scoreboard: {str(e)}",
            ephemeral=True,
        )


class ScoreboardButton(
    discord.ui.DynamicItem[discord.ui.Button],
    template=r"scoreboard:(?P<match_uuid>[a-f0-9-]+)",
):
    """
    Persistent button for viewing match scoreboard.

    Uses DynamicItem to handle button clicks even after bot restarts,
    matching custom_id pattern 'scoreboard:{match_uuid}'.
    """

    def __init__(self, match_uuid: str):
        super().__init__(
            discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="View Scoreboard",
                custom_id=f"scoreboard:{match_uuid}",
            )
        )
        self.match_uuid = match_uuid

    @classmethod
    async def from_custom_id(
        cls, interaction: discord.Interaction, item: discord.ui.Button, match: dict
    ):
        """Reconstruct button from custom_id after bot restart."""
        return cls(match_uuid=match["match_uuid"])

    async def callback(self, interaction: discord.Interaction):
        """Handle button click."""
        await _handle_scoreboard_callback(interaction, self.match_uuid)


class MatchView(discord.ui.View):
    """View with buttons for match messages."""

    def __init__(self, match_url: str, match_uuid: str):
        # timeout=None makes the view persistent
        super().__init__(timeout=None)

        # "Open" button - links to match details on pred.gg
        self.add_item(
            discord.ui.Button(
                style=discord.ButtonStyle.secondary,
                label="Open",
                emoji="🔗",
                url=match_url,
            )
        )

        # "View Scoreboard" button - generates and shows the leaderboard image
        self.add_item(ScoreboardButton(match_uuid))


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
        hero_emoji_mapper: Optional[HeroEmojiMapper] = None,
        role_emoji_mapper: Optional[RoleEmojiMapper] = None,
        subscribed_names: dict[str, str] | None = None
    ) -> None:
        """
        Initialize the match formatter.

        Args:
            match: The match data to format
            subscribed_player_uuids: Set of player UUIDs that should be included
                                    even if they haven't opted in (guild-specific subscriptions)
            hero_emoji_mapper: Optional mapper for hero emojis. If provided, hero emojis will be used.
            role_emoji_mapper: Optional mapper for role emojis. If provided, role emojis will be used.
            subscribed_names: Dict mapping player UUIDs to their stored display names from
                             subscribed_profiles table. Used as fallback when API doesn't provide a name.
        """
        self.match = match
        self.subscribed_player_uuids = subscribed_player_uuids or set()
        self.hero_emoji_mapper = hero_emoji_mapper
        self.role_emoji_mapper = role_emoji_mapper
        self.subscribed_names = subscribed_names or {}
    
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
            A Discord View with action buttons (Open link + View Scoreboard).
        """
        return MatchView(
            match_url=self.match.match_url,
            match_uuid=self.match.match_uuid,
        )
    
    def _build_match_overview(self) -> str:
        """Build the match overview description text."""
        lines = [
            f"**{self.match.score_string}**",
            f"**Duration:** {self.match.duration_minutes} Minutes",
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
    
    def _get_display_name(self, player: MatchPlayerData) -> str:
        """
        Get the display name for a player, using subscribed name as fallback.

        If the player's API name is a UUID-based fallback (e.g., "user-a1b2c3d4...")
        and we have a subscribed name stored, use the subscribed name instead.

        Args:
            player: The player data.

        Returns:
            The best available display name for the player.
        """
        # Check if current name is a UUID fallback (pattern: "user-{8chars}...")
        if (
            player.player_name.startswith("user-")
            and player.player_name.endswith("...")
            and player.player_uuid in self.subscribed_names
        ):
            return self.subscribed_names[player.player_uuid]
        return player.player_name

    def _format_player_line(self, player: MatchPlayerData) -> str:
        """
        Format a single player's stats line.

        Format: +29 [HeroEmoji] [RoleEmoji] **PlayerName** `7/7/3` - `12.7CS/m` - `451G/m` 159.37 PS

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

        # Role emoji (between hero and player name)
        if self.role_emoji_mapper:
            role_display = self.role_emoji_mapper.get_emoji_or_fallback(player.role.value)
            if role_display:  # Only add if not empty (NONE/FILL roles return empty)
                parts.append(role_display)

        # Player name with profile link (use subscribed name as fallback if available)
        display_name = self._get_display_name(player)
        parts.append(f"[**{display_name}**]({player.player_profile_url})")

        # KDA
        parts.append(f"`{player.kda_string}`")

        # CS/m and G/m (per minute stats)
        cs_per_min = calculate_per_minute(player.minions_killed, self.match.duration_seconds)
        gold_per_min = calculate_per_minute(player.gold, self.match.duration_seconds)
        parts.append(f"- `{cs_per_min:.1f}CS/m` - `{gold_per_min:.0f}G/m`")

        # Performance score (if available)
        if player.performance_score is not None:
            parts.append(f"**{player.performance_score:.2f}** PS")

        return " ".join(parts)


def create_match_message(
    match: MatchData,
    subscribed_player_uuids: set[str] | None = None,
    hero_emoji_mapper: Optional[HeroEmojiMapper] = None,
    role_emoji_mapper: Optional[RoleEmojiMapper] = None,
    subscribed_names: dict[str, str] | None = None
) -> tuple[discord.Embed, discord.ui.View]:
    """
    Convenience function to create embed and view for a match.

    Args:
        match: The match data to format.
        subscribed_player_uuids: Set of player UUIDs that should be included
                                even if they haven't opted in (guild-specific subscriptions)
        hero_emoji_mapper: Optional mapper for hero emojis. If provided, hero emojis will be used.
        role_emoji_mapper: Optional mapper for role emojis. If provided, role emojis will be used.
        subscribed_names: Dict mapping player UUIDs to their stored display names from
                         subscribed_profiles table. Used as fallback when API doesn't provide a name.

    Returns:
        Tuple of (embed, view) ready to send.
    """
    formatter = MatchMessageFormatter(
        match, subscribed_player_uuids, hero_emoji_mapper, role_emoji_mapper, subscribed_names
    )
    return formatter.create_embed(), formatter.create_view()

