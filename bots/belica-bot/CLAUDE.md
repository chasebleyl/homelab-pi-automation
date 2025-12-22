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

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | Yes | - | Discord bot token |
| `TEST_GUILD_ID` | No | - | Guild ID for fast slash command sync during dev |
| `PRED_API_URL` | No | https://pred.gg/gql | Predecessor GraphQL API URL |
| `HTTP_PORT` | No | 8080 | Port for HTTP server |
| `DATABASE_URL` | No* | - | PostgreSQL connection URL |
| `DB_HOST` | No* | localhost | Database host |
| `DB_PORT` | No* | 5432 | Database port |
| `DB_NAME` | No* | predecessor | Database name |
| `DB_USER` | No* | postgres | Database user |
| `DB_PASSWORD` | No* | - | Database password |

*Either `DATABASE_URL` or `DB_*` variables required for database features.

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
