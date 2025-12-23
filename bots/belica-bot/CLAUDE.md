# bots/belica-bot

Discord bot for Predecessor game stats and match tracking using discord.py.

## Quick Start

```bash
# From monorepo root
pip install -e ".[dev]"
python bots/belica-bot/bot.py
```

## Structure

```
bots/belica-bot/
├── bot.py              # Main entry - BelicaBot class extends commands.Bot
├── config.py           # Environment variable configuration
├── cogs/
│   ├── general.py      # Info commands (hero lookup, etc.)
│   └── matches.py      # Match tracking slash commands
├── services/
│   ├── channel_config_db.py      # Target channel persistence (PostgreSQL)
│   ├── profile_subscription_db.py # Player subscription persistence
│   ├── match_formatter.py         # Discord embed formatting
│   ├── hero_emoji_mapper.py       # Hero icon to Discord emoji mapping
│   └── http_server.py             # HTTP endpoint for match notifications
└── models/
    └── match.py        # Match data models
```

## Architecture

- **Cogs**: Slash commands organized by feature (general, matches)
- **Services**: Business logic and data access (`*_db.py` = PostgreSQL-backed)
- **HTTP Server**: Receives match notifications from cron workers at `/api/matches`

## Slash Commands

### General (`cogs/general.py`)
- `/ping` - Check bot latency
- `/info` - Display bot information
- `/set-target-channel` - Configure channel for bot posts
- `/remove-target-channel` - Remove target channel
- `/list-target-channels` - List configured channels
- `/clear-target-channels` - Clear all target channels

### Matches (`cogs/matches.py`)
- `/match-preview` - Preview match embed format
- `/match-id <id>` - Fetch and display match by ID
- `/match-profile-subscribe <uuid>` - Subscribe to player's matches
- `/match-profile-unsubscribe <uuid>` - Unsubscribe from player
- `/match-profile-list` - List subscribed profiles

## Environment Variables

See root [CLAUDE.md](../../CLAUDE.md#environment-variables) for all environment variables. Bot-specific:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | - | Discord bot token |
| `TEST_GUILD_ID` | No | - | Guild ID for fast slash command sync |
| `HTTP_PORT` | No | 8080 | Port for HTTP server |

## Dependencies

All dependencies managed in root `pyproject.toml`. Shared packages auto-available:
- `predecessor_api`: API client and services
- `data`: Database connection and repositories

## Key Patterns

### Adding a Slash Command
```python
# In a cog file (cogs/*.py)
@app_commands.command(name="example", description="Example command")
async def example_command(self, interaction: discord.Interaction):
    await interaction.response.send_message("Hello!")
```

### Using the API
```python
# Access via self.bot in cogs
heroes = self.bot.hero_registry.get_all()
```

### Database Access
```python
# Services handle database access
await self.bot.channel_config.set_target_channel(guild_id, channel_id)
await self.bot.profile_subscription.subscribe(guild_id, player_uuid)
```
