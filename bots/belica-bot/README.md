# Belica Bot

Discord bot for [Predecessor](https://www.yourpredecessor.com/) game stats using the [pred.gg](https://pred.gg) GraphQL API.

## Quick Start

```bash
# From monorepo root
pip install -e ".[dev]"
cp .env.example .env
# Edit .env with your Discord token
docker compose up -d postgres
python bots/belica-bot/bot.py
```

See the [monorepo README](../../README.md) for full setup instructions.

## Commands

### General
| Command | Description |
|---------|-------------|
| `/ping` | Check bot latency |
| `/info` | Display bot information |
| `/set-target-channel` | Configure channel for match notifications |
| `/remove-target-channel` | Remove target channel |
| `/list-target-channels` | List configured channels |

### Match Tracking
| Command | Description |
|---------|-------------|
| `/match-preview` | Preview match embed format |
| `/match-id <id>` | Fetch and display match by ID |
| `/match-profile-subscribe <uuid>` | Subscribe to player's matches |
| `/match-profile-unsubscribe <uuid>` | Unsubscribe from player |
| `/match-profile-list` | List subscribed profiles |

## Documentation

See [CLAUDE.md](CLAUDE.md) for detailed architecture and development docs.
