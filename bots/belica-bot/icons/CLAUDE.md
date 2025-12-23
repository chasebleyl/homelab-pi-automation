# icons/

Local cache of game asset icons downloaded from the pred.gg GraphQL API.

## Structure

```
icons/
├── heroes/          # 48 hero portrait icons
│   └── download_hero_icons.py
├── items/           # 233 item icons
│   └── download_item_icons.py
```

## Updating Icons

From the monorepo root with venv activated:

```bash
source .venv/bin/activate

# Re-download all hero icons
python bots/belica-bot/icons/heroes/download_hero_icons.py

# Re-download all item icons
python bots/belica-bot/icons/items/download_item_icons.py
```

Icons are fetched from `https://pred.gg/assets/{asset_id}.png` using asset IDs from the GraphQL API.

## When to Update

- After game patches that add new heroes/items
- If icon assets are updated upstream
