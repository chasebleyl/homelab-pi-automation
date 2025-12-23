"""Match tracking and display commands."""
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone
from typing import Optional
import logging

from predecessor_api import MatchData, MatchPlayerData, TeamSide, GameMode, Region, Role, MatchService, PlayerService
from services import MatchMessageFormatter, ProfileSubscription, HeroEmojiMapper, RoleEmojiMapper
from services.uuid_utils import normalize_uuid, validate_uuid

logger = logging.getLogger("belica.matches")


class Matches(commands.Cog):
    """Commands for match tracking and display."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # Access services from bot instance
        self.hero_registry = getattr(bot, 'hero_registry', None)
        self.profile_subscription: ProfileSubscription = getattr(bot, 'profile_subscription', None)
        # Create services (will be initialized lazily)
        self.match_service: Optional[MatchService] = None
        self.player_service: Optional[PlayerService] = None
    
    @app_commands.command(
        name="match-preview",
        description="Preview how a match embed looks (uses sample data)"
    )
    async def match_preview(self, interaction: discord.Interaction) -> None:
        """
        Display a sample match embed for testing purposes.
        
        This uses hardcoded sample data to demonstrate the embed format.
        If you have subscribed profiles, they will be included in the preview.
        """
        sample_match = self._create_sample_match()
        
        # Get subscribed profiles for this guild if available
        subscribed_uuids = None
        if self.profile_subscription and interaction.guild:
            subscribed_uuids = set(await self.profile_subscription.get_profiles(interaction.guild.id))
        
        # Create emoji mappers if guild or bot is available
        hero_emoji_mapper = None
        role_emoji_mapper = None
        if interaction.guild or self.bot:
            hero_emoji_mapper = HeroEmojiMapper(guild=interaction.guild, bot=self.bot)
            role_emoji_mapper = RoleEmojiMapper(guild=interaction.guild, bot=self.bot)

        formatter = MatchMessageFormatter(sample_match, subscribed_uuids, hero_emoji_mapper, role_emoji_mapper)
        
        embed = formatter.create_embed()
        view = formatter.create_view()
        
        await interaction.response.send_message(embed=embed, view=view)
    
    def _get_match_service(self) -> Optional[MatchService]:
        """Get or create the match service instance."""
        if self.match_service is None:
            api = getattr(self.bot, 'api', None)
            if not api:
                return None
            self.match_service = MatchService(api, self.hero_registry)
        return self.match_service

    def _get_player_service(self) -> Optional[PlayerService]:
        """Get or create the player service instance."""
        if self.player_service is None:
            api = getattr(self.bot, 'api', None)
            if not api:
                return None
            self.player_service = PlayerService(api)
        return self.player_service
    
    @app_commands.command(
        name="match-id",
        description="Fetch and display match details by pred.gg match ID"
    )
    @app_commands.describe(match_id="The match ID from pred.gg (UUID with or without dashes, or numeric ID)")
    async def match_id(self, interaction: discord.Interaction, match_id: str) -> None:
        """Fetch and display match details from pred.gg."""
        await interaction.response.defer()
        
        # Get match service
        match_service = self._get_match_service()
        if not match_service:
            await interaction.followup.send(
                "❌ API client is not available.",
                ephemeral=True
            )
            return
        
        try:
            # Fetch match data
            match = await match_service.fetch_match(match_id)
            
            if not match:
                await interaction.followup.send(
                    f"❌ Match not found. Please check the match ID: `{match_id}`",
                    ephemeral=True
                )
                return
            
            # Get subscribed profiles for this guild if available
            subscribed_uuids = None
            if self.profile_subscription and interaction.guild:
                subscribed_uuids = set(await self.profile_subscription.get_profiles(interaction.guild.id))
            
            # Create emoji mappers if guild or bot is available
            hero_emoji_mapper = None
            role_emoji_mapper = None
            if interaction.guild or self.bot:
                hero_emoji_mapper = HeroEmojiMapper(guild=interaction.guild, bot=self.bot)
                role_emoji_mapper = RoleEmojiMapper(guild=interaction.guild, bot=self.bot)

            # Format and send
            formatter = MatchMessageFormatter(match, subscribed_uuids, hero_emoji_mapper, role_emoji_mapper)
            embed = formatter.create_embed()
            view = formatter.create_view()
            
            await interaction.followup.send(embed=embed, view=view)
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ Error fetching match: {str(e)}",
                ephemeral=True
            )
    
    
    @app_commands.command(
        name="match-profile-subscribe",
        description="Subscribe to a player profile - their matches will be included in match messages"
    )
    @app_commands.describe(player_id="The player UUID from pred.gg (e.g., from a player profile URL)")
    async def match_profile_subscribe(
        self,
        interaction: discord.Interaction,
        player_id: str
    ) -> None:
        """Subscribe to a player profile for match tracking."""
        if not self.profile_subscription:
            await interaction.response.send_message(
                "❌ Profile subscription service is not available.",
                ephemeral=True
            )
            return

        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        # Validate and normalize UUID format
        formatted_uuid = normalize_uuid(player_id)
        if not formatted_uuid:
            await interaction.response.send_message(
                "❌ Invalid player ID format. Please provide a valid UUID from pred.gg.\n"
                "Example: `b16d580e-087c-4cbd-83ee-e9d8e3a8f84c`",
                ephemeral=True
            )
            return

        # Defer response since API validation may take a moment
        await interaction.response.defer(ephemeral=True)

        # Validate player exists via API
        player_service = self._get_player_service()
        if not player_service:
            await interaction.followup.send(
                "❌ API client is not available. Cannot validate player.",
                ephemeral=True
            )
            return

        try:
            player_info = await player_service.validate_player(formatted_uuid)
        except Exception as e:
            logger.error(f"Error validating player {formatted_uuid}: {e}")
            await interaction.followup.send(
                f"❌ Error validating player: {str(e)}",
                ephemeral=True
            )
            return

        if player_info is None:
            await interaction.followup.send(
                f"❌ Player not found. The UUID `{formatted_uuid}` does not exist on pred.gg.\n"
                "Please verify the player UUID from their profile URL.",
                ephemeral=True
            )
            return

        # Player exists - add to subscriptions with their name
        was_new = await self.profile_subscription.add_profile(
            interaction.guild.id, formatted_uuid, player_info.name
        )

        profile_url = f"https://pred.gg/players/{formatted_uuid}"
        player_display = f"**{player_info.name}**" if player_info.name else f"`{formatted_uuid}`"

        if was_new:
            await interaction.followup.send(
                f"✅ Subscribed to {player_display}!\n"
                f"Profile: [View on pred.gg]({profile_url})\n"
                f"Matches including this player will now be shown in match messages.",
                ephemeral=True
            )
        else:
            await interaction.followup.send(
                f"ℹ️ Already subscribed to {player_display}.\n"
                f"Profile: [View on pred.gg]({profile_url})",
                ephemeral=True
            )
    
    @app_commands.command(
        name="match-profile-unsubscribe",
        description="Unsubscribe from a player profile"
    )
    @app_commands.describe(player_id="The player UUID from pred.gg to unsubscribe from")
    async def match_profile_unsubscribe(
        self,
        interaction: discord.Interaction,
        player_id: str
    ) -> None:
        """Unsubscribe from a player profile."""
        if not self.profile_subscription:
            await interaction.response.send_message(
                "❌ Profile subscription service is not available.",
                ephemeral=True
            )
            return
        
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return
        
        # Validate and normalize UUID format
        formatted_uuid = normalize_uuid(player_id)
        if not formatted_uuid:
            await interaction.response.send_message(
                "❌ Invalid player ID format. Please provide a valid UUID from pred.gg.",
                ephemeral=True
            )
            return
        
        was_removed = await self.profile_subscription.remove_profile(interaction.guild.id, formatted_uuid)
        
        if was_removed:
            await interaction.response.send_message(
                f"✅ Unsubscribed from player profile.\n"
                f"Profile: `{formatted_uuid}`",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"ℹ️ This profile is not currently subscribed.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="match-profile-list",
        description="List all subscribed player profiles for this server"
    )
    async def match_profile_list(self, interaction: discord.Interaction) -> None:
        """List all subscribed player profiles for the current server."""
        if not self.profile_subscription:
            await interaction.response.send_message(
                "❌ Profile subscription service is not available.",
                ephemeral=True
            )
            return

        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return

        profiles = await self.profile_subscription.get_profiles_with_names(interaction.guild.id)

        if not profiles:
            await interaction.response.send_message(
                "ℹ️ No player profiles are subscribed for this server.\n"
                "Use `/match-profile-subscribe` to add one.",
                ephemeral=True
            )
            return

        # Build list of profile links with names
        profile_list = []
        for profile in profiles:
            profile_url = f"https://pred.gg/players/{profile.player_uuid}"
            if profile.player_name:
                profile_list.append(f"• **{profile.player_name}** - [`{profile.player_uuid}`]({profile_url})")
            else:
                profile_list.append(f"• [`{profile.player_uuid}`]({profile_url})")

        embed = discord.Embed(
            title="Subscribed Player Profiles",
            description="\n".join(profile_list),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total: {len(profiles)} profile(s)")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    def _get_hero_icon_url(self, hero_name: str) -> str:
        """
        Get the correct icon URL for a hero by name.
        
        Uses hero registry if available, otherwise falls back to a placeholder.
        This is used for sample match data generation.
        
        Args:
            hero_name: The hero's name
            
        Returns:
            Icon URL for the hero
        """
        if self.hero_registry:
            return self.hero_registry.get_icon_url(hero_name)
        # Fallback if registry not available (shouldn't happen in normal operation)
        return f"https://pred.gg/assets/placeholder.png"
    
    def _create_sample_match(self) -> MatchData:
        """Create sample match data for preview purposes."""
        return MatchData(
            match_uuid="440d3105-6a25-465c-9c47-23129ec6d453",
            match_id="440d3105-6a25-465c-9c47-23129ec6d453",
            duration_seconds=2820,  # 47 minutes
            game_mode=GameMode.RANKED,
            region=Region.NA,
            winning_team=TeamSide.DUSK,
            dawn_score=35,
            dusk_score=39,
            end_time=datetime(2025, 12, 9, 23, 40, tzinfo=timezone.utc),
            players=(
                # Dusk team (winners) - 3 opted in
                MatchPlayerData(
                    player_name="Goodnight M00n",
                    player_uuid="b16d580e-087c-4cbd-83ee-e9d8e3a8f84c",
                    hero_name="Countess",
                    hero_icon_url=self._get_hero_icon_url("Countess"),
                    team=TeamSide.DUSK,
                    role=Role.JUNGLE,
                    kills=14, deaths=4, assists=4,
                    minions_killed=187, gold=21450,
                    mmr_change=29,
                    performance_score=159.37,
                    is_opted_in=True,
                ),
                MatchPlayerData(
                    player_name="charvin13",
                    player_uuid="f7ca293e-6cce-49ba-a635-cd52375b9532",
                    hero_name="Dekker",
                    hero_icon_url=self._get_hero_icon_url("Dekker"),
                    team=TeamSide.DUSK,
                    role=Role.SUPPORT,
                    kills=5, deaths=4, assists=18,
                    minions_killed=42, gold=14320,
                    mmr_change=25,
                    performance_score=148.50,
                    is_opted_in=True,
                ),
                MatchPlayerData(
                    player_name="psychomain",
                    player_uuid="23df91be-cb50-4f09-99d6-38f600676492",
                    hero_name="Shinbi",
                    hero_icon_url=self._get_hero_icon_url("Shinbi"),
                    team=TeamSide.DUSK,
                    role=Role.MIDLANE,
                    kills=6, deaths=13, assists=10,
                    minions_killed=289, gold=18750,
                    mmr_change=31,
                    performance_score=105.37,
                    is_opted_in=True,
                ),
                # Dusk team - not opted in
                MatchPlayerData(
                    player_name="SomePlayer1",
                    player_uuid="aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
                    hero_name="Grux",
                    hero_icon_url=self._get_hero_icon_url("Grux"),
                    team=TeamSide.DUSK,
                    role=Role.OFFLANE,
                    kills=8, deaths=5, assists=7,
                    minions_killed=245, gold=17890,
                    mmr_change=27,
                    is_opted_in=False,
                ),
                MatchPlayerData(
                    player_name="SomePlayer2",
                    player_uuid="ffffffff-gggg-hhhh-iiii-jjjjjjjjjjjj",
                    hero_name="Murdock",
                    hero_icon_url=self._get_hero_icon_url("Murdock"),
                    team=TeamSide.DUSK,
                    role=Role.CARRY,
                    kills=6, deaths=9, assists=12,
                    minions_killed=356, gold=22100,
                    mmr_change=24,
                    is_opted_in=False,
                ),
                # Dawn team (losers) - none opted in for this sample
                MatchPlayerData(
                    player_name="DawnPlayer1",
                    player_uuid="11111111-2222-3333-4444-555555555555",
                    hero_name="Sevarog",
                    hero_icon_url=self._get_hero_icon_url("Sevarog"),
                    team=TeamSide.DAWN,
                    role=Role.JUNGLE,
                    kills=7, deaths=8, assists=9,
                    minions_killed=165, gold=16540,
                    mmr_change=-18,
                    is_opted_in=False,
                ),
                MatchPlayerData(
                    player_name="DawnPlayer2",
                    player_uuid="66666666-7777-8888-9999-aaaaaaaaaaaa",
                    hero_name="Narbash",
                    hero_icon_url=self._get_hero_icon_url("Narbash"),
                    team=TeamSide.DAWN,
                    role=Role.SUPPORT,
                    kills=2, deaths=7, assists=15,
                    minions_killed=38, gold=11200,
                    mmr_change=-22,
                    is_opted_in=False,
                ),
                MatchPlayerData(
                    player_name="DawnPlayer3",
                    player_uuid="bbbbbbbb-cccc-dddd-eeee-ffffffffffff",
                    hero_name="Sparrow",
                    hero_icon_url=self._get_hero_icon_url("Sparrow"),
                    team=TeamSide.DAWN,
                    role=Role.CARRY,
                    kills=11, deaths=6, assists=5,
                    minions_killed=312, gold=19870,
                    mmr_change=-15,
                    is_opted_in=False,
                ),
                MatchPlayerData(
                    player_name="DawnPlayer4",
                    player_uuid="00000000-1111-2222-3333-444444444444",
                    hero_name="Gideon",
                    hero_icon_url=self._get_hero_icon_url("Gideon"),
                    team=TeamSide.DAWN,
                    role=Role.MIDLANE,
                    kills=9, deaths=10, assists=8,
                    minions_killed=267, gold=17200,
                    mmr_change=-20,
                    is_opted_in=False,
                ),
                MatchPlayerData(
                    player_name="DawnPlayer5",
                    player_uuid="55555555-6666-7777-8888-999999999999",
                    hero_name="Khaimera",
                    hero_icon_url=self._get_hero_icon_url("Khaimera"),
                    team=TeamSide.DAWN,
                    role=Role.OFFLANE,
                    kills=6, deaths=8, assists=7,
                    minions_killed=198, gold=15430,
                    mmr_change=-19,
                    is_opted_in=False,
                ),
            ),
        )


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(Matches(bot))

