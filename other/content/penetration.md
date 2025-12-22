# Penetration
https://predecessor.wiki.gg/wiki/Penetration

## Overview

Penetration is a base statistic in Predecessor. It's divided into Physical Penetration and Magical Penetration, which respectively penetrate Physical and Magical Armor.

The mechanic determines how much damage bypasses enemy defenses through two distinct categories: Flat Penetration (FP) and Percent Penetration (%P).

## Formula

The effective armor calculation is:

```
Effective Armor = ((Armor Value - Armor Reduction) × (1 - Percent Penetration) - Flat Penetration)
```

### Example

An enemy with 200 armor facing a hero wielding Basilisk (24% Armor Reduction) and Demolisher (28% Percent Penetration and 6 Flat Penetration) would have **103.44** effective armor against that opponent.

## Penetration Types

### Flat Penetration (Lethality)

Flat penetration (Also known as Lethality) is the statistic which can be acquired from items, crests, and abilities such as Wraith's Surprise, Surprise!. Flat penetration is applied after Percentage Penetration.

### Percentage Penetration (Armor Ignore)

Obtainable only from specific items including Demolisher, The Perforator, and Caustica. Applied after Armor Shred but before Flat Penetration.

### Armor Shred (Armor Reduction)

Armor Shred (or Armor Reduction), unlike Flat Penetration and Percentage Penetration, is a temporary debuff that reduces an enemy's Armor for a short duration and is applied before both Flat and Percentage penetrations.

This debuff benefits the applier's teammates as well.
