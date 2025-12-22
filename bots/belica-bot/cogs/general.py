"""General bot commands."""
from typing import Optional
import discord
from discord.ext import commands
from discord import app_commands

from services import ChannelConfig


class General(commands.Cog):
    """General purpose commands."""
    
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # Access channel config from bot instance
        self.channel_config: ChannelConfig = getattr(bot, 'channel_config', None)
    
    @app_commands.command(name="ping", description="Check if the bot is responsive")
    async def ping(self, interaction: discord.Interaction) -> None:
        """Respond with bot latency."""
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"🏓 Pong! Latency: {latency_ms}ms")
    
    @app_commands.command(name="info", description="Display bot information")
    async def info(self, interaction: discord.Interaction) -> None:
        """Display information about the bot."""
        embed = discord.Embed(
            title="Belica Bot",
            description="A Discord bot for Predecessor game stats and information.",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="API",
            value="[pred.gg](https://pred.gg)",
            inline=True
        )
        embed.add_field(
            name="Latency",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(
        name="set-target-channel",
        description="Set this channel as a target channel for bot posts"
    )
    @app_commands.describe(channel="The channel to set as a target (defaults to current channel)")
    @app_commands.default_permissions(manage_channels=True)
    async def set_target_channel(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None
    ) -> None:
        """Set a channel as a target channel for bot posts."""
        if not self.channel_config:
            await interaction.response.send_message(
                "❌ Channel configuration is not available.",
                ephemeral=True
            )
            return
        
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return
        
        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ Target must be a text channel.",
                ephemeral=True
            )
            return
        
        # Check bot permissions
        bot_member = interaction.guild.get_member(self.bot.user.id)
        if bot_member:
            permissions = target_channel.permissions_for(bot_member)
            if not permissions.send_messages or not permissions.embed_links:
                await interaction.response.send_message(
                    f"❌ I don't have permission to send messages or embed links in {target_channel.mention}.",
                    ephemeral=True
                )
                return
        
        was_new = await self.channel_config.add_channel(interaction.guild.id, target_channel.id)
        
        if was_new:
            await interaction.response.send_message(
                f"✅ {target_channel.mention} is now a target channel for bot posts.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"ℹ️ {target_channel.mention} is already configured as a target channel.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="remove-target-channel",
        description="Remove this channel from target channels"
    )
    @app_commands.describe(channel="The channel to remove (defaults to current channel)")
    @app_commands.default_permissions(manage_channels=True)
    async def remove_target_channel(
        self,
        interaction: discord.Interaction,
        channel: Optional[discord.TextChannel] = None
    ) -> None:
        """Remove a channel from target channels."""
        if not self.channel_config:
            await interaction.response.send_message(
                "❌ Channel configuration is not available.",
                ephemeral=True
            )
            return
        
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return
        
        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message(
                "❌ Target must be a text channel.",
                ephemeral=True
            )
            return
        
        was_removed = await self.channel_config.remove_channel(interaction.guild.id, target_channel.id)
        
        if was_removed:
            await interaction.response.send_message(
                f"✅ {target_channel.mention} has been removed from target channels.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"ℹ️ {target_channel.mention} is not configured as a target channel.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="list-target-channels",
        description="List all configured target channels for this server"
    )
    async def list_target_channels(self, interaction: discord.Interaction) -> None:
        """List all configured target channels for the current server."""
        if not self.channel_config:
            await interaction.response.send_message(
                "❌ Channel configuration is not available.",
                ephemeral=True
            )
            return
        
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return
        
        channel_ids = await self.channel_config.get_channels(interaction.guild.id)
        
        if not channel_ids:
            await interaction.response.send_message(
                "ℹ️ No target channels are configured for this server.\n"
                "Use `/set-target-channel` to add one.",
                ephemeral=True
            )
            return
        
        # Build list of channel mentions
        channel_mentions = []
        for channel_id in channel_ids:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                channel_mentions.append(f"• {channel.mention} (`{channel.name}`)")
            else:
                channel_mentions.append(f"• Unknown channel (`{channel_id}`)")
        
        embed = discord.Embed(
            title="Target Channels",
            description="\n".join(channel_mentions),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total: {len(channel_ids)} channel(s)")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="emoji-info",
        description="Get emoji information from a message or emoji"
    )
    @app_commands.describe(emoji="The emoji to get info about (paste the emoji or use <:name:id> format)")
    async def emoji_info(self, interaction: discord.Interaction, emoji: str) -> None:
        """Get information about an emoji, including its ID and usage format."""
        try:
            # Try to parse as Discord emoji format
            if emoji.startswith("<") and emoji.endswith(">"):
                # Format: <:name:id> or <a:name:id>
                is_animated = emoji.startswith("<a:")
                emoji = emoji.strip("<>")
                parts = emoji.split(":")
                if len(parts) == 2:
                    name, emoji_id = parts
                else:
                    await interaction.response.send_message(
                        "❌ Invalid emoji format. Use an emoji or `<:name:id>` format.",
                        ephemeral=True
                    )
                    return
            else:
                # Try to find emoji in bot's cache
                # This is a simple approach - for full parsing, you'd need to extract from message
                await interaction.response.send_message(
                    "❌ Please provide the emoji in `<:name:id>` format, or use Developer Mode to copy the emoji ID.\n"
                    "You can also use `/list-emojis` to see all emojis in this server.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="Emoji Information",
                color=discord.Color.blue()
            )
            embed.add_field(name="Name", value=f"`{name}`", inline=True)
            embed.add_field(name="ID", value=f"`{emoji_id}`", inline=True)
            embed.add_field(name="Animated", value="Yes" if is_animated else "No", inline=True)
            
            static_format = f"<:{name}:{emoji_id}>"
            animated_format = f"<a:{name}:{emoji_id}>"
            usage_format = animated_format if is_animated else static_format
            
            embed.add_field(
                name="Usage Format",
                value=f"`{usage_format}`",
                inline=False
            )
            embed.add_field(
                name="How to Use",
                value=f"Use this in your code:\n```python\nemoji_str = \"{usage_format}\"\n```",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error parsing emoji: {str(e)}\n\n"
                "Tip: Enable Developer Mode, right-click an emoji, and select 'Copy ID'.",
                ephemeral=True
            )
    
    @app_commands.command(
        name="list-emojis",
        description="List all emojis from this server with their IDs"
    )
    async def list_emojis(self, interaction: discord.Interaction) -> None:
        """List all emojis from the current server with their IDs."""
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return
        
        emojis = interaction.guild.emojis
        
        if not emojis:
            await interaction.response.send_message(
                "ℹ️ This server has no custom emojis.",
                ephemeral=True
            )
            return
        
        # Build list of emojis with their IDs
        emoji_list = []
        for emoji in emojis:
            emoji_str = str(emoji)
            emoji_format = f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>"
            emoji_list.append(f"{emoji_str} `{emoji.name}` - ID: `{emoji.id}`\nFormat: {emoji_format}")
        
        # Split into chunks if too long (Discord has 2000 char limit per message)
        chunk_size = 10
        chunks = [emoji_list[i:i + chunk_size] for i in range(0, len(emoji_list), chunk_size)]
        
        for i, chunk in enumerate(chunks):
            embed = discord.Embed(
                title=f"Server Emojis ({len(emojis)} total)" if i == 0 else f"Server Emojis (continued)",
                description="\n\n".join(chunk),
                color=discord.Color.blue()
            )
            if i == 0:
                embed.set_footer(text=f"Showing {min(chunk_size, len(emoji_list))} of {len(emoji_list)}")
            
            if i == 0:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(embed=embed, ephemeral=True)
    
    @app_commands.command(
        name="clear-target-channels",
        description="Clear all target channels for this server"
    )
    @app_commands.default_permissions(manage_channels=True)
    async def clear_target_channels(self, interaction: discord.Interaction) -> None:
        """Clear all target channels for the current server."""
        if not self.channel_config:
            await interaction.response.send_message(
                "❌ Channel configuration is not available.",
                ephemeral=True
            )
            return
        
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )
            return
        
        count = await self.channel_config.clear_guild(interaction.guild.id)
        
        if count > 0:
            await interaction.response.send_message(
                f"✅ Cleared {count} target channel(s) for this server.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "ℹ️ No target channels were configured for this server.",
                ephemeral=True
            )


async def setup(bot: commands.Bot) -> None:
    """Load the cog."""
    await bot.add_cog(General(bot))

