# Itemization Decision Algorithm (Concise)

A compact, repeatable framework for deciding **what to build next** based on opponent, game state, and fight dynamics.

---

## Core Principle

> **Build to change the outcome of the *next* fight, not to optimize a hypothetical later one.**

Every item should solve an *immediate problem* or *enable an immediate advantage*.

---

## Step-by-Step Decision Algorithm

### **STEP 1 — Identify the Enemy’s Next Win Condition**

Ask:

> *How does the opponent beat me in the next 3–5 minutes?*

Choose **one dominant threat**:

* **Burst** (kills you in one rotation)
* **Sustain** (outheals extended fights)
* **DPS / Scaling** (wins long fights later)
* **Utility / Control** (CC, zoning, tempo)

> Focus on what is dangerous **now**, not late game.

---

### **STEP 2 — Identify Why You’re Winning or Losing**

Ask:

> *What is actually causing the gold/XP difference right now?*

Common failure modes:

* Dying too fast
* Losing extended trades
* Losing wave/tempo
* No kill pressure
* Being out-scaled

This prevents buying stats that don’t address the real problem.

---

### **STEP 3 — Check Game State**

Determine your current state:

* **Ahead** → You can buy aggressive, win-accelerating stats
* **Even** → Buy flexible stats, avoid over-committing
* **Behind** → Buy stabilizing stats, reduce variance

> When behind, prioritize **survivability and consistency** over greed.

---

### **STEP 4 — Choose Desired Trade Length**

Ask:

> *Do I want fights to be short or long?*

* **Short trades (1–3s):** burst, damage amplification, ability haste
* **Long trades (5–10s):** sustain, %HP damage, on-hit effects

Never mix trade philosophies unintentionally.

---

### **STEP 5 — Buy the Minimal Stat Package**

Choose the **smallest set of stats** that:

* Counters the enemy win condition (Step 1)
* Fixes your current problem (Step 2)
* Matches your game state (Step 3)
* Supports desired trade length (Step 4)

> Do **not** buy stats that won’t matter in the next fight.

---

## Quick Stat Mapping

| Problem                | Stat Focus                |
| ---------------------- | ------------------------- |
| Burst deaths           | Max HP + relevant resist  |
| Losing to sustain      | Anti-heal **or** burst    |
| Losing extended fights | DPS **or** disengage      |
| No kill pressure       | Power + amplification     |
| Losing tempo           | Ability haste / waveclear |

---

## Algorithm-to-Tag Mapping

Use this table to translate algorithm concepts into item tags for filtering items_tagged.json:

| Algorithm Concept              | Relevant Tags                                                      |
| ------------------------------ | ------------------------------------------------------------------ |
| Counter Burst win condition    | `anti_burst`, `max_hp`, `physical_mitigation`, `magical_mitigation`|
| Counter Sustain win condition  | `anti_heal`, `burst_damage`                                        |
| Counter DPS/Scaling            | `burst_damage`, `anti_burst`, `kite_tool`                          |
| Counter Utility/Control        | `tenacity`, `spellshield`, `stickiness`                            |
| Dying too fast                 | `anti_burst`, `max_hp`, `physical_mitigation`, `magical_mitigation`|
| Losing extended trades         | `sustained_damage`, `on_hit`, `pct_max_hp_damage`, `sustain`       |
| Losing wave/tempo              | `ability_haste`, `tempo`                                           |
| No kill pressure               | `burst_damage`, `damage_amplification`                             |
| Being out-scaled               | `burst_damage`, `damage_amplification`, `high_variance`            |
| Short trades (1–3s)            | `burst_damage`, `damage_amplification`, `ability_haste`, `anti_burst` |
| Long trades (5–10s)            | `sustained_damage`, `on_hit`, `pct_max_hp_damage`, `sustain`, `stickiness` |
| Ahead (win-accelerate)         | `burst_damage`, `damage_amplification`, `high_variance`, `scaling` |
| Behind (stabilize)             | `anti_burst`, `max_hp`, `sustain`; avoid `high_variance`, `scaling`|

---

## Specialty Tags

Some tags require specific context to be valuable:

- **`spellshield`** — Counter to Utility/Control when the enemy has a single high-impact ability or CC (e.g., Gideon ult, Riktor hook). Less valuable against sustained CC chains.
- **`tenacity`** — Counter to Utility/Control when enemy relies on multiple CC abilities in sequence. Reduces total lockdown duration.
- **`high_variance`** — Strong when ahead, weak when behind. Avoid if stabilizing; embrace if snowballing.
- **`dueling_power`** — Prioritize in 1v1 contexts (default). Deprioritize if next fight is a teamfight.
- **`scaling`** — Items with permanent stacking or late-game power spikes. Avoid when behind or needing immediate impact.

---

## One-Line Decision Rule

> **Counter how they win next, fix why you’re losing now, and buy only what affects the next fight.**

---

## Ultra-Compact Checklist (In-Game Use)

```
1. How do they win the next fight?
2. Why am I losing or winning right now?
3. Am I ahead, even, or behind?
4. Do I want short or long trades?
5. Buy the smallest stat package that answers 1–4.
```

---

*Use this algorithm every time you recall. It scales across heroes, roles, and metas.*
