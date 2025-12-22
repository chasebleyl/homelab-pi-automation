# Belica Bot Setup

## Installation

### Automated Installation (Recommended)

The `predecessor-api-client` package is automatically installed when you install dependencies from `requirements.txt`:

```bash
cd belica-bot
pip install -r requirements.txt
```

This will automatically install:
- All Python dependencies (discord.py, aiohttp, etc.)
- The shared `predecessor-api-client` package in editable mode from `../predecessor-api-client`

### Alternative: Install with pyproject.toml

If you prefer to use `pyproject.toml`:

```bash
cd belica-bot
pip install -e .
# Then manually install the shared package:
pip install -e ../predecessor-api-client
```

## Development

The `predecessor-api-client` package is automatically installed via `requirements.txt` using an editable install (`-e ../predecessor-api-client`). This approach:

- Works automatically when running `pip install -r requirements.txt`
- Works across different machines and operating systems (no hardcoded paths)
- Ensures the package is properly installed and available to all Python processes
- Changes to the shared package are immediately available (editable install)

## Project Structure

```
cb-discord-bots/
├── predecessor-api-client/     # Shared API client package
│   ├── predecessor_api/
│   │   ├── __init__.py
│   │   ├── client.py           # PredecessorAPI class
│   │   └── models.py           # Hero, HeroRegistry models
│   └── pyproject.toml
└── belica-bot/                  # Discord bot
    ├── cogs/
    ├── models/                  # Bot-specific models (MatchData, etc.)
    ├── services/
    └── pyproject.toml           # References predecessor-api-client
```
