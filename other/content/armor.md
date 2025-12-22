# Armor
https://predecessor.wiki.gg/wiki/Armor

## Overview

Armor is a base statistic in Predecessor. It is divided into Physical Armor and Magical Armor and the stats respectively reduce Physical Damage and Magical Damage taken.

## Damage Received

The damage calculation follows this formula:

```
Damage Received = (Physical/Magical Power × Attack/Ability Scaling % × Critical Hit Damage %)
                 × (100 / (Effective Armor Value + 100))
```

**Example:** An enemy dealing 200 raw damage to a player with 60 armor results in 125 damage taken.

## Resistance Percentage

The resistance formula is:

```
Armor Resistance % = 1 - 100/(100 + Effective Armor)
```

Every point of Armor roughly calculates into 1% effective max Health against the specific damage type.

### Resistance Scaling Table

| Armor | Resistance |
|-------|-----------|
| 11 | 10% |
| 25 | 20% |
| 50 | 33% |
| 67 | 40% |
| 100 | 50% |
| 200 | 67% |
| 300 | 75% |

## Effective Armor

After applying penetration effects:

```
Effective Armor = (Armor × (1 - Percent Armor Reduction) - Flat Armor Reduction)
                 × (1 - Percent Penetration) - Flat Penetration
```

**Example:** 100 armor against an enemy with 30% penetration and 10 flat penetration = 60 effective armor.
