# BTU Gacha — BlackTower Universe Gacha Bot

**BTU Gacha** is a private Discord gacha bot where users can pull for collectible character cards from my boyfriend's original story universe, *Blacktower Universe (BTU)*. This project is solely for entertainment and learning purposes, with no intention of marketing whatsoever.

---

## ✨ What can you do ?

- 🎴 **Pull** for character cards at random — limited to **3 pulls per day**
- 📖 **Browse your binder** to check your collection
- 🔍 **Inspect cards** you've obtained for lore and details
- 🔄 **Convert duplicates** into free guaranteed higher-tier pulls
- 🎟️ **Use free pulls** stored from converted duplicates

---

## 📋 Commands

| Command | Description |
|---|---|
| `!help` | Lists all available commands |
| `!pull` | Pull a random character card (limited to 3/day) |
| `!binder` | Open your card collection |
| `!info <card_id>` | Get detailed info on a card you own |
| `!check` | Check your remaining daily pulls and reset timer |
| `!convert <card_id>` | Convert 10 duplicates into 1 free higher-tier pull |
| `!fpull` | Use a stored free pull |
| `!fpcheck` | Check your available free pulls |

> 💡 Card IDs are visible in your `!binder`.

---

## 🔒 Admin Commands

A set of commands is reserved for users with the **God** role for bot control and debugging purposes. These include managing user binders, resetting daily limits, and adding free pulls manually. Use `!devhelp` to see the full list if you have the role.

---

## 🎟️ Free Pull System

When you accumulate **10 duplicates** of the same card, you can convert them into a **free pull** that doesn't count toward your daily limit — and guarantees a card of a **higher tier** than the one converted.

**How it works:**
- `!convert <card_id>` — converts 10 duplicates into 1 stored free pull
- The free pull's minimum guaranteed tier is based on the converted card's tier
- You can convert multiples of 10 at once (20 duplicates = 2 free pulls, etc.)
- Free pulls are stored and can be used anytime with `!fpull`

> *Example: Converting 10 copies of a **D tier** card guarantees your free pull will land on **C tier or higher**. The rarer the converted card, the better the boosted rates.*

---

## 🌟 Tiers & Rarities

Cards are ranked across **9 tiers**, from most common to rarest:

| Tier | Rarity | Pull Rate |
|---|---|---|
| **E** | Common | ~39.89% |
| **D** | Uncommon | ~25% |
| **C** | Rare | ~15% |
| **B** | Epic | ~10% |
| **A** | Super Epic | ~6% |
| **S** | Legendary | ~3% |
| **SS** | Mythic | ~1% |
| **???** | *(Secret)* | 🤫 |
| **???** | *(Secret)* | 🤫 |

> The last two tiers are secret. You'll know them when you see them — if you're lucky enough. 👀

Higher rarities may contain **alternative arts** of lower rarity characters.

---

## 🔮 Upcoming Features

- 🧠 **Knowledge quiz** on the books and characters
- 🤝 **Trading system** between users

---

*BTU Gacha is a passion project. All characters and artwork belong to their original creator.*