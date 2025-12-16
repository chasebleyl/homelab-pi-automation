# Setup Guide

## Prerequisites

- Python 3.11+
- Discord bot token ([Developer Portal](https://discord.com/developers/applications))

## Installation

### macOS / Raspberry Pi OS

```bash
cd belica-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create `.env` from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your Discord bot token:

```
DISCORD_TOKEN=your_token_here
```

## Discord Bot Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application → name it "Belica" (or your choice)
3. Go to **Bot** → Reset Token → Copy it to your `.env`
4. Enable **Message Content Intent** under Privileged Gateway Intents
5. Go to **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Embed Links`, `Use Slash Commands`
6. Open the generated URL to invite the bot to your server

## Running

```bash
source .venv/bin/activate
python bot.py
```

### Run as Background Service (Raspberry Pi)

Create `/etc/systemd/system/belica-bot.service`:

```ini
[Unit]
Description=Belica Discord Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/belica-bot
ExecStart=/home/pi/belica-bot/.venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable belica-bot
sudo systemctl start belica-bot
```

View logs:

```bash
journalctl -u belica-bot -f
```

## Channel Configuration

By default, the bot can respond to commands in any channel. However, if you want to restrict where the bot posts automatic updates or match notifications, you can configure target channels.

### Setting Target Channels

1. **Set a target channel**: Use the `/set-target-channel` command in the channel where you want the bot to post
   - Requires "Manage Channels" permission
   - You can optionally specify a different channel: `/set-target-channel channel:#channel-name`

2. **List target channels**: Use `/list-target-channels` to see all configured channels for your server

3. **Remove a target channel**: Use `/remove-target-channel` to remove a channel from the list
   - Requires "Manage Channels" permission

4. **Clear all target channels**: Use `/clear-target-channels` to remove all configured channels
   - Requires "Manage Channels" permission

### How It Works

- The bot stores channel configurations per server (guild) in `channel_config.json`
- If no channels are configured, the bot can post anywhere (current behavior)
- If channels are configured, you can use `bot.is_target_channel(channel)` in your code to check if posting is allowed
- The configuration persists across bot restarts

### Example Usage in Code

```python
# In your cog or command handler
if bot.is_target_channel(channel):
    await channel.send("This will only post in configured channels")
else:
    # Handle case where channel is not configured
    pass
```

