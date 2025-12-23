"""Generate detailed leaderboard images for match results."""
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

from predecessor_api import format_player_display_name, calculate_per_minute, name_to_slug


class LeaderboardImageGenerator:
    """Generates detailed leaderboard images from match data."""

    # Colors
    BG_COLOR = (26, 26, 46)  # Dark blue-gray
    VICTORY_HEADER = (34, 52, 43)  # Dark green tint
    DEFEAT_HEADER = (52, 34, 38)  # Dark red tint
    ROW_COLOR_1 = (32, 34, 44)  # Alternating row
    ROW_COLOR_2 = (38, 40, 52)  # Alternating row
    TEXT_PRIMARY = (255, 255, 255)  # White
    TEXT_SECONDARY = (160, 160, 170)  # Gray
    TEXT_MUTED = (100, 100, 110)  # Darker gray
    DMG_DEALT_COLOR = (255, 140, 90)  # Orange
    DMG_TAKEN_COLOR = (100, 160, 255)  # Blue
    GOLD_COLOR = (255, 215, 0)  # Gold

    # Rank colors
    RANK_COLORS = {
        "Bronze": (180, 110, 70),
        "Silver": (160, 170, 180),
        "Gold": (255, 200, 80),
        "Platinum": (80, 200, 180),
        "Diamond": (120, 180, 255),
        "Master": (180, 100, 220),
        "Grandmaster": (255, 80, 80),
    }

    # Base layout constants (at scale 1.0)
    BASE_WIDTH = 1020
    BASE_ROW_HEIGHT = 50
    BASE_HEADER_HEIGHT = 30
    BASE_TEAM_HEADER_HEIGHT = 25
    BASE_ICON_SIZE = 36
    BASE_ITEM_ICON_SIZE = 18
    BASE_CREST_ICON_SIZE = 38
    BASE_AUGMENT_ICON_SIZE = 20
    BASE_PADDING = 8

    # Base font sizes (at scale 1.0)
    BASE_FONT_LARGE = 16
    BASE_FONT_MEDIUM = 13
    BASE_FONT_SMALL = 10

    # Role sort order by team
    DUSK_ROLE_ORDER = ["CARRY", "SUPPORT", "MIDLANE", "JUNGLE", "OFFLANE"]
    DAWN_ROLE_ORDER = ["OFFLANE", "JUNGLE", "MIDLANE", "SUPPORT", "CARRY"]

    # Base column widths and positions (at scale 1.0)
    BASE_COLUMNS = {
        "rank": (0, 80),        # Rank badge
        "hero": (80, 50),       # Hero icon
        "name": (130, 120),     # Player name
        "kda": (250, 100),      # K/D/A
        "dmg_dealt": (350, 100),# Damage dealt
        "dmg_taken": (450, 100),# Damage taken
        "wards": (550, 70),     # Wards P/D
        "cs": (620, 80),        # CS
        "gold": (700, 100),     # Gold
        "augments": (800, 80),  # Augments (3 at 20px + spacing)
        "items": (880, 140),    # Items (crest + 3 cols items + consumables col)
    }

    def __init__(self, icons_dir: Optional[Path] = None, scale: float = 1.5):
        """Initialize the generator.

        Args:
            icons_dir: Path to icons directory containing heroes/ subfolder
            scale: Scale factor for image resolution (1.0 = 1000px wide, 1.5 = 1500px, 2.0 = 2000px)
        """
        self.scale = scale
        self.icons_dir = icons_dir or Path(__file__).parent.parent / "icons"
        self.hero_icons_dir = self.icons_dir / "heroes"
        self.role_icons_dir = self.icons_dir / "roles"
        self.item_icons_dir = self.icons_dir / "items"
        self.augment_icons_dir = self.icons_dir / "augments"

        # Compute scaled layout constants
        self.WIDTH = int(self.BASE_WIDTH * scale)
        self.ROW_HEIGHT = int(self.BASE_ROW_HEIGHT * scale)
        self.HEADER_HEIGHT = int(self.BASE_HEADER_HEIGHT * scale)
        self.TEAM_HEADER_HEIGHT = int(self.BASE_TEAM_HEADER_HEIGHT * scale)
        self.ICON_SIZE = int(self.BASE_ICON_SIZE * scale)
        self.ITEM_ICON_SIZE = int(self.BASE_ITEM_ICON_SIZE * scale)
        self.CREST_ICON_SIZE = int(self.BASE_CREST_ICON_SIZE * scale)
        self.AUGMENT_ICON_SIZE = int(self.BASE_AUGMENT_ICON_SIZE * scale)
        self.PADDING = int(self.BASE_PADDING * scale)

        # Compute scaled column positions and widths
        self.COLUMNS = {
            name: (int(x * scale), int(w * scale))
            for name, (x, w) in self.BASE_COLUMNS.items()
        }

        # Try to load fonts, fall back to default
        self._load_fonts()

    def _s(self, value: int) -> int:
        """Scale a pixel value by the current scale factor."""
        return int(value * self.scale)

    def _get_role_icon(self, role: str) -> Optional[Image.Image]:
        """Load role icon from local cache."""
        # Convert role to lowercase filename
        role_slug = role.lower()
        if role_slug in ("none", "fill", ""):
            return None

        icon_path = self.role_icons_dir / f"{role_slug}.png"

        if icon_path.exists():
            try:
                icon = Image.open(icon_path).convert("RGBA")
                # Role icons are smaller, overlay size (scaled)
                role_size = int(12 * self.scale)
                icon = icon.resize((role_size, role_size), Image.Resampling.LANCZOS)
                return icon
            except Exception:
                pass
        return None

    def _load_fonts(self):
        """Load fonts for rendering with scaled sizes."""
        # Compute scaled font sizes
        font_size_large = int(self.BASE_FONT_LARGE * self.scale)
        font_size_medium = int(self.BASE_FONT_MEDIUM * self.scale)
        font_size_small = int(self.BASE_FONT_SMALL * self.scale)

        # Bundled Inter font (preferred)
        fonts_dir = Path(__file__).parent.parent / "fonts"
        inter_regular = fonts_dir / "Inter-Regular.ttf"
        inter_medium = fonts_dir / "Inter-Medium.ttf"
        inter_bold = fonts_dir / "Inter-Bold.ttf"

        # Try bundled Inter font first
        if inter_regular.exists():
            try:
                self.font_large = ImageFont.truetype(str(inter_bold), font_size_large)
                self.font_medium = ImageFont.truetype(str(inter_medium), font_size_medium)
                self.font_small = ImageFont.truetype(str(inter_regular), font_size_small)
                return
            except (OSError, IOError):
                pass

        # Fallback to system fonts
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "C:/Windows/Fonts/arial.ttf",  # Windows
        ]

        self.font_large = None
        self.font_medium = None
        self.font_small = None

        for font_path in font_paths:
            try:
                self.font_large = ImageFont.truetype(font_path, font_size_large)
                self.font_medium = ImageFont.truetype(font_path, font_size_medium)
                self.font_small = ImageFont.truetype(font_path, font_size_small)
                break
            except (OSError, IOError):
                continue

        # Fall back to default font if none found
        if self.font_large is None:
            self.font_large = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_small = ImageFont.load_default()

    def _get_hero_icon(self, hero_name: str) -> Optional[Image.Image]:
        """Load hero icon from local cache."""
        slug = name_to_slug(hero_name)
        icon_path = self.hero_icons_dir / f"{slug}.png"

        if icon_path.exists():
            try:
                icon = Image.open(icon_path)
                icon = icon.resize((self.ICON_SIZE, self.ICON_SIZE), Image.Resampling.LANCZOS)
                return icon
            except Exception:
                pass
        return None

    def _get_item_icon(self, item_name: str, size: int = 24) -> Optional[Image.Image]:
        """Load item icon from local cache.

        Args:
            item_name: The item's display name
            size: Size to resize icon to (default 24px for items column)

        Returns:
            Resized RGBA image or None if not found
        """
        slug = name_to_slug(item_name)
        icon_path = self.item_icons_dir / f"{slug}.png"

        if icon_path.exists():
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon = icon.resize((size, size), Image.Resampling.LANCZOS)
                return icon
            except Exception:
                pass
        return None

    def _get_augment_icon(self, augment_name: str, size: int = 20) -> Optional[Image.Image]:
        """Load augment icon from local cache.

        Args:
            augment_name: The augment's display name
            size: Size to resize icon to (default 20px for augments column)

        Returns:
            Resized RGBA image or None if not found
        """
        slug = name_to_slug(augment_name)
        icon_path = self.augment_icons_dir / f"{slug}.png"

        if icon_path.exists():
            try:
                icon = Image.open(icon_path).convert("RGBA")
                icon = icon.resize((size, size), Image.Resampling.LANCZOS)
                return icon
            except Exception:
                pass
        return None

    def _get_rank_color(self, tier_name: str) -> tuple:
        """Get color for rank tier."""
        return self.RANK_COLORS.get(tier_name, self.TEXT_SECONDARY)

    def _sort_players_by_role(self, players: list, team: str) -> list:
        """Sort players by role order for the given team."""
        role_order = self.DUSK_ROLE_ORDER if team == "DUSK" else self.DAWN_ROLE_ORDER

        def get_role_index(player):
            role = player.get("role", "NONE").upper()
            try:
                return role_order.index(role)
            except ValueError:
                return len(role_order)  # Unknown roles go last

        return sorted(players, key=get_role_index)

    def generate(self, match_data: dict) -> bytes:
        """Generate leaderboard image from match data.

        Args:
            match_data: Match data dict (from GraphQL response or cached fixture)

        Returns:
            PNG image as bytes
        """
        match = match_data.get("match", match_data)
        duration_seconds = match["duration"]
        winning_team = match["winningTeam"]
        players = match["matchPlayers"]
        end_time_str = match.get("endTime")  # ISO 8601 format, e.g., "2025-12-23T03:49:35Z"

        # Split players by team and sort by role
        dusk_players = self._sort_players_by_role(
            [p for p in players if p["team"] == "DUSK"], "DUSK"
        )
        dawn_players = self._sort_players_by_role(
            [p for p in players if p["team"] == "DAWN"], "DAWN"
        )

        # Calculate image height
        num_rows = len(players)
        height = (
            self.HEADER_HEIGHT +  # Column headers
            self.TEAM_HEADER_HEIGHT +  # "VICTORY - DUSK"
            len(dusk_players) * self.ROW_HEIGHT +
            self.TEAM_HEADER_HEIGHT +  # "DEFEAT - DAWN"
            len(dawn_players) * self.ROW_HEIGHT +
            self.PADDING
        )

        # Create image
        img = Image.new("RGB", (self.WIDTH, height), self.BG_COLOR)
        draw = ImageDraw.Draw(img)

        y = 0

        # Draw column headers with match time info
        y = self._draw_column_headers(draw, y, duration_seconds, end_time_str)

        # Draw winning team
        if winning_team == "DUSK":
            y = self._draw_team_section(img, draw, y, "VICTORY", "DUSK", dusk_players, duration_seconds, True)
            y = self._draw_team_section(img, draw, y, "DEFEAT", "DAWN", dawn_players, duration_seconds, False)
        else:
            y = self._draw_team_section(img, draw, y, "VICTORY", "DAWN", dawn_players, duration_seconds, True)
            y = self._draw_team_section(img, draw, y, "DEFEAT", "DUSK", dusk_players, duration_seconds, False)

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

    def _draw_column_headers(
        self, draw: ImageDraw.Draw, y: int, duration_seconds: int, end_time_str: Optional[str] = None
    ) -> int:
        """Draw column header row with match time info."""
        # Format match duration
        duration_minutes = duration_seconds // 60
        duration_secs = duration_seconds % 60
        duration_text = f"{duration_minutes}:{duration_secs:02d}"

        # Format end time in Eastern timezone if available
        if end_time_str:
            try:
                # Parse ISO 8601 UTC time
                end_time_utc = datetime.fromisoformat(end_time_str.replace("Z", "+00:00"))
                # Convert to Eastern time
                eastern = ZoneInfo("America/New_York")
                end_time_et = end_time_utc.astimezone(eastern)
                # Format: "YYYY-MM-DD HH:MM AM/PM ET - match lasted MM:SS"
                time_text = f"{end_time_et.strftime('%Y-%m-%d %I:%M %p')} ET - match lasted {duration_text}"
            except (ValueError, TypeError):
                time_text = f"Match lasted {duration_text}"
        else:
            time_text = f"Match lasted {duration_text}"

        draw.text(
            (self.PADDING, y + self._s(8)),
            time_text,
            fill=self.TEXT_SECONDARY,
            font=self.font_small
        )

        headers = [
            ("rank", ""),
            ("hero", ""),
            ("name", ""),
            ("kda", "K / D / A"),
            ("dmg_dealt", "DMG DEALT"),
            ("dmg_taken", "DMG TAKEN"),
            ("wards", "WARDS"),
            ("cs", "CS"),
            ("gold", "GOLD"),
            ("augments", "AUGS"),
            ("items", "ITEMS"),
        ]

        for col_name, text in headers:
            if text:
                x, width = self.COLUMNS[col_name]
                draw.text(
                    (x + self.PADDING, y + self._s(8)),
                    text,
                    fill=self.TEXT_MUTED,
                    font=self.font_small
                )

        return y + self.HEADER_HEIGHT

    def _draw_team_section(
        self,
        img: Image.Image,
        draw: ImageDraw.Draw,
        y: int,
        result: str,
        team: str,
        players: list,
        duration_seconds: int,
        is_winner: bool
    ) -> int:
        """Draw a team's section (header + player rows)."""
        # Team header background
        header_color = self.VICTORY_HEADER if is_winner else self.DEFEAT_HEADER
        draw.rectangle(
            [(0, y), (self.WIDTH, y + self.TEAM_HEADER_HEIGHT)],
            fill=header_color
        )

        # Calculate team totals
        total_kills = sum(p["kills"] for p in players)
        total_deaths = sum(p["deaths"] for p in players)
        total_assists = sum(p["assists"] for p in players)

        # Team header text
        header_text = f"{result} - {team}  {total_kills} / {total_deaths} / {total_assists}"
        draw.text(
            (self.PADDING, y + self._s(5)),
            header_text,
            fill=self.TEXT_PRIMARY,
            font=self.font_medium
        )

        y += self.TEAM_HEADER_HEIGHT

        # Draw player rows
        for i, player in enumerate(players):
            row_color = self.ROW_COLOR_1 if i % 2 == 0 else self.ROW_COLOR_2
            y = self._draw_player_row(img, draw, y, player, duration_seconds, row_color)

        return y

    def _draw_player_row(
        self,
        img: Image.Image,
        draw: ImageDraw.Draw,
        y: int,
        player: dict,
        duration_seconds: int,
        row_color: tuple
    ) -> int:
        """Draw a single player row."""
        # Row background
        draw.rectangle(
            [(0, y), (self.WIDTH, y + self.ROW_HEIGHT)],
            fill=row_color
        )

        # Extract player data
        player_info = player.get("player", {})
        hero_data = player.get("heroData", {}) or player.get("hero", {})
        rating = player.get("rating", {})
        rank = rating.get("rank", {}) if rating else {}

        player_name = format_player_display_name(
            player_info.get("name"),
            player_info.get("uuid")
        )
        hero_name = hero_data.get("displayName") or hero_data.get("name", "Unknown")

        kills = player.get("kills", 0)
        deaths = player.get("deaths", 0)
        assists = player.get("assists", 0)
        hero_damage = player.get("heroDamage", 0)
        damage_taken = player.get("heroDamageTaken", 0)
        wards_placed = player.get("wardsPlaced", 0)
        wards_destroyed = player.get("wardsDestroyed", 0)
        minions = player.get("minionsKilled", 0) + player.get("neutralMinionsKilled", 0)
        gold = player.get("gold", 0)

        tier_name = rank.get("tierName", "")
        rank_name = rank.get("name", "")
        vp = rating.get("newPoints", 0) if rating else 0

        # Calculate derived stats
        kda = (kills + assists) / max(deaths, 1)
        dps_dealt = calculate_per_minute(hero_damage, duration_seconds)
        dps_taken = calculate_per_minute(damage_taken, duration_seconds)
        cs_per_min = calculate_per_minute(minions, duration_seconds)
        gold_per_min = calculate_per_minute(gold, duration_seconds)

        row_center_y = y + self.ROW_HEIGHT // 2

        # 1. Rank badge
        x, width = self.COLUMNS["rank"]
        if rank_name:
            rank_color = self._get_rank_color(tier_name)
            draw.text(
                (x + self.PADDING, row_center_y - self._s(10)),
                rank_name,
                fill=rank_color,
                font=self.font_small
            )
            draw.text(
                (x + self.PADDING, row_center_y + self._s(2)),
                f"{int(vp)} VP",
                fill=self.TEXT_MUTED,
                font=self.font_small
            )

        # 2. Hero icon with role overlay
        x, width = self.COLUMNS["hero"]
        icon = self._get_hero_icon(hero_name)
        if icon:
            icon_x = x + self._s(4)
            icon_y = row_center_y - self.ICON_SIZE // 2

            # Convert hero icon to RGBA for compositing
            if icon.mode != "RGBA":
                icon = icon.convert("RGBA")

            # Get role icon and overlay it
            role = player.get("role", "NONE")
            role_icon = self._get_role_icon(role)

            if role_icon:
                # Create a copy to avoid modifying cached icon
                icon_with_role = icon.copy()
                # Position role icon at bottom-right corner
                role_x = self.ICON_SIZE - role_icon.width
                role_y = self.ICON_SIZE - role_icon.height

                # Draw circular black background behind role icon
                role_bg_size = role_icon.width + self._s(4)
                role_bg = Image.new("RGBA", (role_bg_size, role_bg_size), (0, 0, 0, 0))
                role_bg_draw = ImageDraw.Draw(role_bg)
                role_bg_draw.ellipse(
                    [(0, 0), (role_bg_size - 1, role_bg_size - 1)],
                    fill=(0, 0, 0, 255)
                )
                # Paste background then role icon
                bg_x = role_x - self._s(2)
                bg_y = role_y - self._s(2)
                icon_with_role.paste(role_bg, (bg_x, bg_y), role_bg)
                icon_with_role.paste(role_icon, (role_x, role_y), role_icon)

                img.paste(icon_with_role, (icon_x, icon_y), icon_with_role)
            else:
                img.paste(icon, (icon_x, icon_y), icon)

        # 3. Player name
        x, width = self.COLUMNS["name"]
        draw.text(
            (x + self.PADDING, row_center_y - self._s(8)),
            player_name[:15],  # Truncate long names
            fill=self.TEXT_PRIMARY,
            font=self.font_medium
        )

        # 4. K/D/A
        x, width = self.COLUMNS["kda"]
        kda_text = f"{kills} / {deaths} / {assists}"
        draw.text(
            (x + self.PADDING, row_center_y - self._s(10)),
            kda_text,
            fill=self.TEXT_PRIMARY,
            font=self.font_medium
        )
        draw.text(
            (x + self.PADDING, row_center_y + self._s(4)),
            f"{kda:.1f} KDA",
            fill=self.TEXT_SECONDARY,
            font=self.font_small
        )

        # 5. Damage Dealt
        x, width = self.COLUMNS["dmg_dealt"]
        draw.text(
            (x + self.PADDING, row_center_y - self._s(10)),
            f"{hero_damage:,}",
            fill=self.DMG_DEALT_COLOR,
            font=self.font_medium
        )
        draw.text(
            (x + self.PADDING, row_center_y + self._s(4)),
            f"{dps_dealt:.0f} DPS",
            fill=self.TEXT_MUTED,
            font=self.font_small
        )

        # 6. Damage Taken
        x, width = self.COLUMNS["dmg_taken"]
        draw.text(
            (x + self.PADDING, row_center_y - self._s(10)),
            f"{damage_taken:,}",
            fill=self.DMG_TAKEN_COLOR,
            font=self.font_medium
        )
        draw.text(
            (x + self.PADDING, row_center_y + self._s(4)),
            f"{dps_taken:.0f} DPS",
            fill=self.TEXT_MUTED,
            font=self.font_small
        )

        # 7. Wards
        x, width = self.COLUMNS["wards"]
        draw.text(
            (x + self.PADDING, row_center_y - self._s(6)),
            f"{wards_placed} / {wards_destroyed}",
            fill=self.TEXT_PRIMARY,
            font=self.font_medium
        )

        # 8. CS
        x, width = self.COLUMNS["cs"]
        draw.text(
            (x + self.PADDING, row_center_y - self._s(10)),
            f"{minions}",
            fill=self.TEXT_PRIMARY,
            font=self.font_medium
        )
        draw.text(
            (x + self.PADDING, row_center_y + self._s(4)),
            f"{cs_per_min:.1f}/m",
            fill=self.TEXT_MUTED,
            font=self.font_small
        )

        # 9. Gold
        x, width = self.COLUMNS["gold"]
        draw.text(
            (x + self.PADDING, row_center_y - self._s(10)),
            f"{gold:,}",
            fill=self.GOLD_COLOR,
            font=self.font_medium
        )
        draw.text(
            (x + self.PADDING, row_center_y + self._s(4)),
            f"{gold_per_min:.0f}/m",
            fill=self.TEXT_MUTED,
            font=self.font_small
        )

        # 10. Augments (perks)
        x, width = self.COLUMNS["augments"]
        perk_data = player.get("perkData", []) or []

        # Sort perks: HERO_SPECIFIC_1 first, then COMMON_1, then COMMON_2
        slot_order = {"HERO_SPECIFIC_1": 0, "COMMON_1": 1, "COMMON_2": 2}
        sorted_perks = sorted(
            perk_data,
            key=lambda p: slot_order.get(p.get("slot", ""), 99)
        )

        aug_x = x + self.PADDING
        aug_y = row_center_y - self.AUGMENT_ICON_SIZE // 2
        aug_spacing = self._s(2)  # Space between augments

        for perk in sorted_perks[:3]:  # Max 3 augments
            if perk:
                augment_name = perk.get("displayName", "")
                if augment_name:
                    aug_icon = self._get_augment_icon(augment_name, self.AUGMENT_ICON_SIZE)
                    if aug_icon:
                        img.paste(aug_icon, (aug_x, aug_y), aug_icon)
            aug_x += self.AUGMENT_ICON_SIZE + aug_spacing

        # 11. Items (crest + build items + consumables)
        x, width = self.COLUMNS["items"]
        inventory_items = player.get("inventoryItemData", []) or []

        # Separate items by slot type
        crest_item = None
        passive_items = []  # Regular build items
        active_item = None  # Potion or jungle knife
        trinket_item = None  # Ward
        for item_data in inventory_items:
            if item_data:
                slot_type = item_data.get("slotType", "")
                if slot_type == "CREST":
                    crest_item = item_data
                elif slot_type == "ACTIVE":
                    active_item = item_data
                elif slot_type == "TRINKET":
                    trinket_item = item_data
                else:  # PASSIVE or unknown
                    passive_items.append(item_data)

        item_spacing = self._s(2)  # Space between items
        crest_x = x + self.PADDING

        # Render crest icon (larger, spanning both rows)
        if crest_item:
            crest_name = crest_item.get("displayName", "")
            if crest_name:
                crest_icon = self._get_item_icon(crest_name, self.CREST_ICON_SIZE)
                if crest_icon:
                    crest_y = row_center_y - self.CREST_ICON_SIZE // 2
                    img.paste(crest_icon, (crest_x, crest_y), crest_icon)

        # Calculate starting x position for build items (after crest)
        items_start_x = crest_x + self.CREST_ICON_SIZE + item_spacing + self._s(2)

        # Row positions
        row1_y = row_center_y - self.ITEM_ICON_SIZE - self._s(1)
        row2_y = row_center_y + self._s(1)

        # Render passive items in 2 rows of 3 (columns 1-3)
        # Row 1: first 3 passive items
        item_x = items_start_x
        for item_data in passive_items[:3]:
            if item_data:
                item_name = item_data.get("displayName", "")
                if item_name:
                    item_icon = self._get_item_icon(item_name, self.ITEM_ICON_SIZE)
                    if item_icon:
                        img.paste(item_icon, (item_x, row1_y), item_icon)
            item_x += self.ITEM_ICON_SIZE + item_spacing

        # Row 2: next 3 passive items
        item_x = items_start_x
        for item_data in passive_items[3:6]:
            if item_data:
                item_name = item_data.get("displayName", "")
                if item_name:
                    item_icon = self._get_item_icon(item_name, self.ITEM_ICON_SIZE)
                    if item_icon:
                        img.paste(item_icon, (item_x, row2_y), item_icon)
            item_x += self.ITEM_ICON_SIZE + item_spacing

        # Column 4: Consumables (active item on top, trinket/ward on bottom)
        consumable_x = items_start_x + 3 * (self.ITEM_ICON_SIZE + item_spacing)

        # Row 1: Active item (potion or jungle knife)
        if active_item:
            active_name = active_item.get("displayName", "")
            if active_name:
                active_icon = self._get_item_icon(active_name, self.ITEM_ICON_SIZE)
                if active_icon:
                    img.paste(active_icon, (consumable_x, row1_y), active_icon)

        # Row 2: Trinket (ward)
        if trinket_item:
            trinket_name = trinket_item.get("displayName", "")
            if trinket_name:
                trinket_icon = self._get_item_icon(trinket_name, self.ITEM_ICON_SIZE)
                if trinket_icon:
                    img.paste(trinket_icon, (consumable_x, row2_y), trinket_icon)

        return y + self.ROW_HEIGHT


def generate_leaderboard_image(
    match_data: dict,
    icons_dir: Optional[Path] = None,
    scale: float = 1.5
) -> bytes:
    """Convenience function to generate a leaderboard image.

    Args:
        match_data: Match data dict
        icons_dir: Optional path to icons directory
        scale: Scale factor for image resolution (1.0 = 1000px wide, 1.5 = 1500px, 2.0 = 2000px)

    Returns:
        PNG image as bytes
    """
    generator = LeaderboardImageGenerator(icons_dir, scale=scale)
    return generator.generate(match_data)
