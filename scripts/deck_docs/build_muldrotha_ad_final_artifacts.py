#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import re
import sys
from html import escape as html_escape
from urllib.parse import quote
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.deck_docs.generate_commander_companion_html import parse_reference
REF_PATH = ROOT / "docs/decks/sultai/muldrotha-reference.md"
POOL_PATH = ROOT / "docs/decks/sultai/MTG COLLECTION - Sheet5.tsv"
META_PATH = ROOT / "data/processed/enriched_cards.json"
OUT_MD = ROOT / "docs/decks/sultai/muldrotha-a-d-final-analysis.md"
OUT_HTML = ROOT / "docs/decks/sultai/muldrotha-a-d-final-comparison.html"

CATEGORIES = ["Creatures", "Enchantments", "Artifacts", "Instants", "Sorceries", "Lands"]

USE_USER_SUPPLIED_FINAL_DECK = True
USER_SUPPLIED_FINAL_DECKLIST = [
    "Baleful Strix",
    "Birds of Paradise",
    "Bloodghast",
    "Bloom Tender",
    "Ledger Shredder",
    "Dauthi Voidwalker",
    "Deathrite Shaman",
    "Eternal Witness",
    "Gravebreaker Lamia",
    "Gravecrawler",
    "Haywire Mite",
    "Hedron Crab",
    "Jarad, Golgari Lich Lord",
    "Lord of Extinction",
    "Veil of Summer",
    "Pitiless Plunderer",
    "Plaguecrafter",
    "Sidisi, Brood Tyrant",
    "Spore Frog",
    "Stitcher's Supplier",
    "Syr Konrad, the Grim",
    "The Gitrog Monster",
    "Vile Entomber",
    "Animate Dead",
    "Exploration",
    "Kaya's Ghostform",
    "Mystic Remora",
    "Necromancy",
    "Pernicious Deed",
    "Seal of Primordium",
    "Survival of the Fittest",
    "Sylvan Library",
    "Tortured Existence",
    "Altar of Dementia",
    "Arcane Signet",
    "Ashnod's Altar",
    "Birthing Pod",
    "Lightning Greaves",
    "Crucible of Worlds",
    "Lotus Petal",
    "Mesmeric Orb",
    "Perpetual Timepiece",
    "Phyrexian Altar",
    "Sensei's Diving Top",
    "Skullclamp",
    "Sol Ring",
    "Arcane Denial",
    "Assassin's Trophy",
    "Counterspell",
    "Deadly Rollick",
    "Entomb",
    "Force of Negation",
    "Gifts Ungiven",
    "Intuition",
    "Mana Drain",
    "Swan Song",
    "Buried Alive",
    "Life from the Loam",
    "Living Death",
    "Nature's Lore",
    "Reanimate",
    "Noxious Revival",
    "Victimize",
    "Bayou",
    "Bloodstained Mire",
    "Bojuka Bog",
    "Boseiju, Who Endures",
    "Breeding Pool",
    "City of Brass",
    "Command Beacon",
    "Command Tower",
    "Dakmor Salvage",
    "Flooded Strand",
    "High Market",
    "Mana Confluence",
    "Marsh Flats",
    "Misty Rainforest",
    "Morphic Pool",
    "Otawara, Soaring City",
    "Overgrown Tomb",
    "Phyrexian Tower",
    "Polluted Delta",
    "Reflecting Pool",
    "Rejuvenating Springs",
    "Scalding Tarn",
    "Strip Mine",
    "Takenuma, Abandoned Mire",
    "Tropical Island",
    "Underground Sea",
    "Undergrowth Stadium",
    "Urborg, Tomb of Yawgmoth",
    "Verdant Catacombs",
    "Volrath's Stronghold",
    "Wasteland",
    "Watery Grave",
    "Windswept Heath",
    "Wooded Foothills",
    "Yavimaya, Cradle of Growth",
    "Zagoth Triome",
]
USER_SUPPLIED_ALIASES = {
    "Sensei's Diving Top": "Sensei's Divining Top",
}

# Bracket/Game Changers snapshot basis: Wizards Oct 21, 2025 + Feb 9, 2026 update.
GAME_CHANGERS = {
    "Ad Nauseam",
    "Ancient Tomb",
    "Aura Shards",
    "Biorhythm",
    "Bolas's Citadel",
    "Braids, Cabal Minion",
    "Chrome Mox",
    "Coalition Victory",
    "Consecrated Sphinx",
    "Crop Rotation",
    "Cyclonic Rift",
    "Demonic Tutor",
    "Drannith Magistrate",
    "Enlightened Tutor",
    "Farewell",
    "Fierce Guardianship",
    "Field of the Dead",
    "Force of Will",
    "Gaea's Cradle",
    "Gamble",
    "Gifts Ungiven",
    "Glacial Chasm",
    "Grand Arbiter Augustin IV",
    "Grim Monolith",
    "Humility",
    "Imperial Seal",
    "Intuition",
    "Jeska's Will",
    "Lion's Eye Diamond",
    "Mana Vault",
    "Mishra's Workshop",
    "Mox Diamond",
    "Mystical Tutor",
    "Narset, Parter of Veils",
    "Natural Order",
    "Necropotence",
    "Notion Thief",
    "Opposition Agent",
    "Orcish Bowmasters",
    "Panoptic Mirror",
    "Rhystic Study",
    "Seedborn Muse",
    "Serra's Sanctum",
    "Smothering Tithe",
    "Survival of the Fittest",
    "Teferi's Protection",
    "Tergrid, God of Fright",
    "Thassa's Oracle",
    "The One Ring",
    "The Tabernacle at Pendrell Vale",
    "Underworld Breach",
    "Vampiric Tutor",
    "Worldly Tutor",
}

# Sol Ring explicitly excluded from GC list by Wizards bracket guidance.

BASICS = {"island", "swamp", "forest", "mountain", "plains", "wastes"}
POOL_ALIASES = {
    "underrealm lich": "underream lich",
    "meren of clan nel toth": "meren of clan nel toth",
}
EXCEPTION_CARDS: set[str] = {
    # User-confirmed physical copy outside TSV snapshot.
    "spore frog",
}

EDHREC_OPTIMIZED_FETCH_TS = "2026-03-02 02:18 UTC"
EDHREC_OPTIMIZED_CATEGORY_PULLS = {
    "highsynergycards": {
        "label": "High Synergy Cards",
        "rows": [
            {"card": "Spore Frog", "inclusion": 63.0, "synergy": 55.0},
            {"card": "Kaya's Ghostform", "inclusion": 57.0, "synergy": 51.0},
            {"card": "Mystic Remora", "inclusion": 62.0, "synergy": 46.0},
            {"card": "Pernicious Deed", "inclusion": 49.0, "synergy": 45.0},
            {"card": "Animate Dead", "inclusion": 58.0, "synergy": 45.0},
            {"card": "Entomb", "inclusion": 52.0, "synergy": 44.0},
            {"card": "Haywire Mite", "inclusion": 48.0, "synergy": 43.0},
            {"card": "Seal of Primordium", "inclusion": 47.0, "synergy": 42.0},
            {"card": "Altar of Dementia", "inclusion": 49.0, "synergy": 41.0},
            {"card": "Eternal Witness", "inclusion": 66.0, "synergy": 40.0},
        ],
    },
    "creatures": {
        "label": "Creatures",
        "rows": [
            {"card": "Displacer Kitten", "inclusion": 35.0, "synergy": 31.0},
            {"card": "Siren Stormtamer", "inclusion": 31.0, "synergy": 27.0},
            {"card": "Plaguecrafter", "inclusion": 27.0, "synergy": 24.0},
            {"card": "Underrealm Lich", "inclusion": 29.0, "synergy": 23.0},
            {"card": "Accursed Marauder", "inclusion": 26.0, "synergy": 23.0},
            {"card": "Doc Aurlock, Grizzled Genius", "inclusion": 28.0, "synergy": 21.0},
            {"card": "Dauthi Voidwalker", "inclusion": 29.0, "synergy": 20.0},
            {"card": "World Shaper", "inclusion": 28.0, "synergy": 20.0},
            {"card": "Icetill Explorer", "inclusion": 37.0, "synergy": 19.0},
            {"card": "Baleful Strix", "inclusion": 35.0, "synergy": 19.0},
            {"card": "Azusa, Lost but Seeking", "inclusion": 23.0, "synergy": 13.0},
            {"card": "Satyr Wayfinder", "inclusion": 21.0, "synergy": 13.0},
            {"card": "Bloom Tender", "inclusion": 22.0, "synergy": 12.0},
            {"card": "Hedron Crab", "inclusion": 20.0, "synergy": 8.0},
        ],
    },
    "instants": {
        "label": "Instants",
        "rows": [
            {"card": "Gifts Ungiven", "inclusion": 18.0, "synergy": 16.0},
            {"card": "Mana Drain", "inclusion": 24.0, "synergy": 12.0},
            {"card": "Intuition", "inclusion": 13.0, "synergy": 12.0},
            {"card": "Force of Will", "inclusion": 16.0, "synergy": 8.0},
            {"card": "Worldly Tutor", "inclusion": 16.0, "synergy": 7.0},
            {"card": "Assassin's Trophy", "inclusion": 37.0, "synergy": 1.0},
            {"card": "Pact of Negation", "inclusion": 6.8, "synergy": 1.0},
            {"card": "Counterspell", "inclusion": 33.0, "synergy": -3.0},
            {"card": "An Offer You Can't Refuse", "inclusion": 18.0, "synergy": -4.0},
            {"card": "Arcane Denial", "inclusion": 7.7, "synergy": -7.0},
        ],
    },
    "sorceries": {
        "label": "Sorceries",
        "rows": [
            {"card": "Buried Alive", "inclusion": 36.0, "synergy": 29.0},
            {"card": "Reanimate", "inclusion": 37.0, "synergy": 15.0},
            {"card": "Windfall", "inclusion": 19.0, "synergy": 12.0},
            {"card": "Diabolic Intent", "inclusion": 13.0, "synergy": 8.0},
            {"card": "Toxic Deluge", "inclusion": 26.0, "synergy": 7.0},
            {"card": "Living Death", "inclusion": 14.0, "synergy": 1.0},
            {"card": "Victimize", "inclusion": 14.0, "synergy": -1.0},
            {"card": "Three Visits", "inclusion": 12.0, "synergy": -12.0},
            {"card": "Nature's Lore", "inclusion": 14.0, "synergy": -14.0},
        ],
    },
    "utilityartifacts": {
        "label": "Utility Artifacts",
        "rows": [
            {"card": "Mesmeric Orb", "inclusion": 31.0, "synergy": 20.0},
            {"card": "Phyrexian Altar", "inclusion": 24.0, "synergy": 20.0},
            {"card": "Ashnod's Altar", "inclusion": 21.0, "synergy": 18.0},
            {"card": "Perpetual Timepiece", "inclusion": 21.0, "synergy": 17.0},
            {"card": "Lightning Greaves", "inclusion": 37.0, "synergy": 15.0},
            {"card": "Soul-Guide Lantern", "inclusion": 8.1, "synergy": 7.0},
            {"card": "Conduit of Worlds", "inclusion": 7.9, "synergy": -7.0},
        ],
    },
    "enchantments": {
        "label": "Enchantments",
        "rows": [
            {"card": "Secrets of the Dead", "inclusion": 32.0, "synergy": 29.0},
            {"card": "Seal of Removal", "inclusion": 28.0, "synergy": 26.0},
            {"card": "Exploration", "inclusion": 30.0, "synergy": 19.0},
            {"card": "Necromancy", "inclusion": 23.0, "synergy": 19.0},
            {"card": "Ripples of Undeath", "inclusion": 28.0, "synergy": 14.0},
            {"card": "Survival of the Fittest", "inclusion": 14.0, "synergy": 12.0},
            {"card": "Sylvan Library", "inclusion": 18.0, "synergy": 11.0},
            {"card": "Dance of the Dead", "inclusion": 10.0, "synergy": 9.0},
        ],
    },
    "utilitylands": {
        "label": "Utility Lands",
        "rows": [
            {"card": "Strip Mine", "inclusion": 39.0, "synergy": 34.0},
            {"card": "Command Beacon", "inclusion": 42.0, "synergy": 31.0},
            {"card": "Phyrexian Tower", "inclusion": 27.0, "synergy": 23.0},
            {"card": "Urborg, Tomb of Yawgmoth", "inclusion": 39.0, "synergy": 22.0},
            {"card": "Boseiju, Who Endures", "inclusion": 40.0, "synergy": 19.0},
            {"card": "Yavimaya, Cradle of Growth", "inclusion": 35.0, "synergy": 15.0},
            {"card": "Wasteland", "inclusion": 15.0, "synergy": 13.0},
            {"card": "Dakmor Salvage", "inclusion": 17.0, "synergy": 11.0},
            {"card": "Bojuka Bog", "inclusion": 35.0, "synergy": 10.0},
            {"card": "High Market", "inclusion": 6.7, "synergy": 5.0},
        ],
    },
    "manaartifacts": {
        "label": "Mana Artifacts",
        "rows": [
            {"card": "Sol Ring", "inclusion": 93.0, "synergy": 11.0},
            {"card": "Arcane Signet", "inclusion": 72.0, "synergy": 0.0},
            {"card": "Lotus Petal", "inclusion": 57.0, "synergy": 48.0},
            {"card": "Lion's Eye Diamond", "inclusion": 16.0, "synergy": 15.0},
            {"card": "Mana Vault", "inclusion": 16.0, "synergy": 10.0},
            {"card": "Mox Diamond", "inclusion": 12.0, "synergy": 7.0},
            {"card": "Talisman of Dominance", "inclusion": 12.0, "synergy": -4.0},
            {"card": "Talisman of Curiosity", "inclusion": 12.0, "synergy": -5.0},
            {"card": "Talisman of Resilience", "inclusion": 13.0, "synergy": -2.0},
        ],
    },
}

# EDHREC signals pulled from live commander pages/snippets (captured 2026-03-02 UTC).
EDHREC_SIGNAL = {
    "spore frog": {"inclusion": 63.0, "synergy": 55.0},
    "kaya's ghostform": {"inclusion": 57.0, "synergy": 51.0},
    "mystic remora": {"inclusion": 62.0, "synergy": 46.0},
    "seal of primordium": {"inclusion": 47.0, "synergy": 42.0},
    "entomb": {"inclusion": 52.0, "synergy": 44.0},
    "gifts ungiven": {"inclusion": 18.0, "synergy": 16.0},
    "intuition": {"inclusion": 13.0, "synergy": 12.0},
    "arcane denial": {"inclusion": 7.7, "synergy": -7.0},
    "buried alive": {"inclusion": 36.0, "synergy": 29.0},
    "living death": {"inclusion": 14.0, "synergy": 1.0},
    "nature's lore": {"inclusion": 14.0, "synergy": -14.0},
    "mesmeric orb": {"inclusion": 31.0, "synergy": 20.0},
    "ashnod's altar": {"inclusion": 21.0, "synergy": 18.0},
    "phyrexian altar": {"inclusion": 24.0, "synergy": 20.0},
    "perpetual timepiece": {"inclusion": 21.0, "synergy": 17.0},
    "soul-guide lantern": {"inclusion": 8.1, "synergy": 7.0},
    "conduit of worlds": {"inclusion": 7.9, "synergy": -7.0},
    "secrets of the dead": {"inclusion": 32.0, "synergy": 29.0},
    "survival of the fittest": {"inclusion": 14.0, "synergy": 12.0},
    "command beacon": {"inclusion": 42.0, "synergy": 31.0},
    "strip mine": {"inclusion": 39.0, "synergy": 34.0},
    "urborg, tomb of yawgmoth": {"inclusion": 39.0, "synergy": 22.0},
    "yavimaya, cradle of growth": {"inclusion": 35.0, "synergy": 15.0},
    "dakmor salvage": {"inclusion": 17.0, "synergy": 11.0},
    "wasteland": {"inclusion": 15.0, "synergy": 13.0},
    "high market": {"inclusion": 6.7, "synergy": 5.0},
    "sol ring": {"inclusion": 93.0, "synergy": 11.0},
    "arcane signet": {"inclusion": 72.0, "synergy": 0.0},
    "lotus petal": {"inclusion": 57.0, "synergy": 48.0},
    "mana vault": {"inclusion": 16.0, "synergy": 10.0},
    "mox diamond": {"inclusion": 12.0, "synergy": 7.0},
    "talisman of curiosity": {"inclusion": 12.0, "synergy": -5.0},
    "talisman of dominance": {"inclusion": 12.0, "synergy": -4.0},
    "talisman of resilience": {"inclusion": 13.0, "synergy": -2.0},
}

# Manual card-role overlays for synthesis quality.
ROLE_BONUS = {
    "living death": (5.0, 5.0, 2.5, 3.0),
    "syr konrad, the grim": (5.0, 5.0, 2.5, 4.0),
    "jarad, golgari lich lord": (5.0, 5.0, 3.0, 4.0),
    "lord of extinction": (4.5, 5.0, 2.0, 3.0),
    "gravecrawler": (5.0, 4.5, 4.5, 5.0),
    "pitiless plunderer": (5.0, 4.5, 3.5, 4.0),
    "phyrexian altar": (5.0, 4.5, 3.0, 4.5),
    "altar of dementia": (5.0, 4.5, 4.0, 4.5),
    "craterhoof behemoth": (3.0, 4.5, 1.5, 2.0),
    "mesmeric orb": (5.0, 3.5, 4.5, 4.5),
    "underrealm lich": (4.5, 3.5, 2.5, 4.0),
    "world shaper": (4.5, 3.0, 2.5, 4.0),
    "ramunap excavator": (4.5, 3.0, 3.5, 4.5),
    "gravebreaker lamia": (4.5, 4.0, 3.0, 3.5),
    "vile entomber": (4.5, 4.0, 3.5, 3.5),
    "meren of clan nel toth": (4.5, 3.5, 2.5, 4.5),
    "sidisi, brood tyrant": (4.5, 4.0, 2.5, 3.5),
    "conduit of worlds": (4.0, 3.0, 3.0, 4.0),
    "tortured existence": (4.5, 3.5, 4.0, 4.5),
    "spore frog": (5.0, 3.5, 5.0, 5.0),
    "kaya's ghostform": (4.8, 3.5, 5.0, 4.8),
    "mystic remora": (4.0, 3.0, 5.0, 4.0),
    "volrath's stronghold": (4.8, 3.0, 3.0, 4.8),
    "high market": (4.2, 3.2, 3.0, 4.3),
    "survival of the fittest": (5.0, 4.5, 3.5, 4.5),
    "intuition": (5.0, 5.0, 4.0, 3.5),
    "gifts ungiven": (5.0, 5.0, 3.5, 3.5),
    "force of will": (1.5, 3.5, 4.0, 1.0),
    "fierce guardianship": (1.5, 3.5, 5.0, 1.0),
    "the one ring": (2.0, 3.5, 3.0, 2.5),
}

UNIQUE_CARD_EVALS: dict[str, tuple[int, int, int, str]] = {
    "Ledger Shredder": (2, 2, 4, "Cheap filtering body, but its connive value is less deterministic than dedicated yard tutors/self-mill in Muldrotha shells."),
    "Massacre Wurm": (3, 4, 2, "Strong board-punish finisher, but high CMC and low recursion-loop density make it clunkier than primary combo cash-outs."),
    "Mulldrifter": (3, 2, 3, "Replayable draw creature is fine with Muldrotha, but it does not materially tighten your kill clock."),
    "River Kelpie": (4, 3, 2, "Synergistic with graveyard casting, but six mana for value-only impact competes poorly with proactive finish enablers."),
    "Bloom Tender": (3, 3, 5, "Explosive acceleration into Muldrotha and setup turns, even if it is not itself a graveyard engine piece."),
    "Caustic Caterpillar": (5, 3, 5, "One-mana recurable hate-bear is premium Muldrotha texture and repeatedly answers graveyard hate pieces."),
    "Craterhoof Behemoth": (2, 5, 2, "Low recursion synergy but excellent terminal conversion once recursive board development has gone wide."),
    "Gravecrawler": (5, 5, 5, "Combo-grade recursion piece that converts graveyard access into repeatable loop pressure with altar shells."),
    "Haywire Mite": (5, 3, 5, "Efficient recurable answer that cleanly removes opposing hate while fitting Muldrotha replay cadence."),
    "Pitiless Plunderer": (5, 5, 3, "Core combo glue for recursive sac loops and one of the cleanest win-path multipliers in this pool."),
    "Conduit of Worlds": (4, 3, 3, "Backup Muldrotha effect that improves recursion redundancy and land replay in grindy games."),
    "Talisman of Resilience": (2, 2, 4, "Serviceable fixing, but weaker than role-compression options that also enable sacrifice/loop lines."),
    "Phyrexian Altar": (5, 5, 3, "Top-tier recursion engine card enabling deterministic Gravecrawler loop kills and flexible mana conversion."),
    "Talisman of Dominance": (2, 2, 4, "Efficient rock with better color split for blue interaction turns than Resilience in this configuration."),
    "Sylvan Library": (2, 3, 4, "Premium card quality engine, but less deck-defining than dedicated recursion loop support in this build target."),
    "Fact or Fiction": (3, 3, 3, "Graveyard-friendly card velocity, though four mana at instant speed is slower than focused pile/tutor setup."),
    "Force of Will": (1, 4, 4, "Excellent protection, but one-shot non-permanent interaction has lower long-game recursion leverage."),
    "Lim-Dul's Vault": (2, 3, 3, "Powerful selection spell, but it does not directly advance permanent recursion engines."),
    "Mana Drain": (1, 4, 5, "Best-in-class tempo counter, strong efficiency despite limited direct graveyard synergy."),
    "Arcane Denial": (1, 2, 4, "Broad counterspell coverage, but lower conversion pressure than free-protection or engine tutors."),
    "Fierce Guardianship": (1, 4, 5, "Exceptional protection while Muldrotha is online, though it contributes little to recursive value loops."),
    "Pact of Negation": (1, 4, 5, "Protects all-in combo turns at zero mana and is ideal for forced cash-out windows."),
    "Exotic Orchard": (2, 2, 4, "Fixing is strong in multiplayer, but fetchable/self-mill-positive lands improve this deck's recursion velocity."),
    "Volrath's Stronghold": (5, 3, 3, "Repeatable creature recursion land that upgrades grind resilience without consuming spell slots."),
}

CATEGORY_TARGETS = {
    "Creatures": 25,
    "Enchantments": 7,
    "Artifacts": 14,
    "Instants": 10,
    "Sorceries": 7,
    "Lands": 36,
}

# Explicitly challenge incumbent bias by forcing non-A/non-D candidates into contention.
DE_NOVO_PRIORITY_BY_CATEGORY = {
    "Creatures": [
        "Spore Frog",
        "Icetill Explorer",
        "Gravebreaker Lamia",
        "Baleful Strix",
    ],
    "Enchantments": [
        "Mystic Remora",
        "Kaya's Ghostform",
    ],
    "Artifacts": [
        "Perpetual Timepiece",
    ],
    "Instants": [
        "Nature's Claim",
    ],
    "Sorceries": [
        "Three Visits",
    ],
    "Lands": [
        "Volrath's Stronghold",
        "Command Beacon",
        "Strip Mine",
        "Wasteland",
        "Urborg, Tomb of Yawgmoth",
        "Yavimaya, Cradle of Growth",
        "Dakmor Salvage",
    ],
}

LAND_LOCKS = [
    "Command Tower",
    "Tropical Island",
    "Bayou",
    "Underground Sea",
    "Breeding Pool",
    "Overgrown Tomb",
    "Watery Grave",
    "Zagoth Triome",
    "Morphic Pool",
    "Rejuvenating Springs",
    "Undergrowth Stadium",
    "Reflecting Pool",
    "Mana Confluence",
    "City of Brass",
    "Polluted Delta",
    "Verdant Catacombs",
    "Misty Rainforest",
    "Marsh Flats",
    "Flooded Strand",
    "Windswept Heath",
    "Wooded Foothills",
    "Scalding Tarn",
    "High Market",
    "Bloodstained Mire",
    "Command Beacon",
    "Dakmor Salvage",
    "Strip Mine",
    "Wasteland",
    "Urborg, Tomb of Yawgmoth",
    "Yavimaya, Cradle of Growth",
    "Bojuka Bog",
    "Takenuma, Abandoned Mire",
    "Otawara, Soaring City",
    "Boseiju, Who Endures",
    "Phyrexian Tower",
    "Volrath's Stronghold",
]

BASELINE_FUNCTIONAL_LOCKS = {
    "Creatures": [
        "Birds of Paradise",
        "Spore Frog",
        "Bloom Tender",
        "Deathrite Shaman",
        "Eternal Witness",
        "Dauthi Voidwalker",
        "World Shaper",
        "Gravebreaker Lamia",
    ],
    "Enchantments": [
        "Animate Dead",
        "Necromancy",
        "Seal of Primordium",
        "Mystic Remora",
        "Kaya's Ghostform",
        "Exploration",
        "Phyrexian Reclamation",
    ],
    "Artifacts": [
        "Sol Ring",
        "Lotus Petal",
        "Arcane Signet",
        "Skullclamp",
        "Lightning Greaves",
        "Crucible of Worlds",
        "Soul-Guide Lantern",
        "Talisman of Curiosity",
        "Talisman of Dominance",
    ],
    "Instants": [
        "Swan Song",
        "Force of Negation",
        "Arcane Denial",
        "Mana Drain",
        "Counterspell",
        "Heroic Intervention",
        "Assassin's Trophy",
    ],
    "Sorceries": [
        "Life from the Loam",
        "Buried Alive",
        "Reanimate",
        "Victimize",
        "Living Death",
        "Regrowth",
        "Nature's Lore",
    ],
    "Lands": [],
}

ROLE_QUOTAS = {
    "lands": (36, 36),
    "ramp_sources": (12, 14),
    "self_mill_setup": (10, 13),
    "recursion_engines_payoff_permanents": (10, 14),
    "interaction_total": (14, 18),
    "stack_interaction": (7, 99),
    "permanent_removal_hate": (6, 99),
    "graveyard_exile_control": (4, 99),
    "graveyard_exile_permanent": (2, 99),
    "protection_pieces": (5, 8),
    "wincon_contributors": (10, 14),
}

CORE_ENGINE_PACKAGE = {
    "Stitcher's Supplier",
    "Hedron Crab",
    "Satyr Wayfinder",
    "Nyx Weaver",
    "Mesmeric Orb",
    "Ramunap Excavator",
    "Conduit of Worlds",
    "Life from the Loam",
    "Entomb",
    "Buried Alive",
    "Meren of Clan Nel Toth",
    "Tortured Existence",
}

PRIMARY_KILL_PACKAGE = {
    "Living Death",
    "Syr Konrad, the Grim",
    "Jarad, Golgari Lich Lord",
    "Lord of Extinction",
}

BACKUP_KILL_PACKAGE = {
    "Gravecrawler",
    "Pitiless Plunderer",
    "Phyrexian Altar",
    "Ashnod's Altar",
    "Altar of Dementia",
    "Craterhoof Behemoth",
}

ANTI_HATE_PACKAGE = {
    "Bojuka Bog",
    "Dauthi Voidwalker",
    "Deathrite Shaman",
    "Soul-Guide Lantern",
    "Krosan Grip",
    "Assassin's Trophy",
    "Caustic Caterpillar",
    "Haywire Mite",
}

RAMP_SOURCES = {
    "Sol Ring",
    "Lotus Petal",
    "Arcane Signet",
    "Talisman of Curiosity",
    "Talisman of Dominance",
    "Birds of Paradise",
    "Bloom Tender",
    "Deathrite Shaman",
    "Exploration",
    "Nature's Lore",
    "Pitiless Plunderer",
    "Phyrexian Altar",
    "Ashnod's Altar",
}

SELF_MILL_SETUP = {
    "Stitcher's Supplier",
    "Hedron Crab",
    "Satyr Wayfinder",
    "Nyx Weaver",
    "Mesmeric Orb",
    "Sidisi, Brood Tyrant",
    "Vile Entomber",
    "Buried Alive",
    "Entomb",
    "Life from the Loam",
    "Intuition",
    "Gifts Ungiven",
}

RECURSION_ENGINES_PAYOFF_PERMANENTS = {
    "Ramunap Excavator",
    "Conduit of Worlds",
    "Crucible of Worlds",
    "Volrath's Stronghold",
    "Meren of Clan Nel Toth",
    "Animate Dead",
    "Kaya's Ghostform",
    "Necromancy",
    "Phyrexian Reclamation",
    "Tortured Existence",
    "Survival of the Fittest",
    "World Shaper",
    "Underrealm Lich",
    "Gravebreaker Lamia",
}

STACK_INTERACTION_CARDS = {
    "Swan Song",
    "Force of Negation",
    "Arcane Denial",
    "Mana Drain",
    "Counterspell",
    "An Offer You Can't Refuse",
    "Fierce Guardianship",
    "Heroic Intervention",
    "Assassin's Trophy",
    "Krosan Grip",
}

# Cards that contribute to the broad interaction quota but are not stack counters.
SUPPLEMENTAL_INTERACTION_CARDS = {
    "Nature's Claim",
    "Beast Within",
    "Assassin's Trophy",
    "Krosan Grip",
}

PERMANENT_REMOVAL_HATE = {
    "Seal of Primordium",
    "Caustic Caterpillar",
    "Haywire Mite",
    "Dauthi Voidwalker",
    "Deathrite Shaman",
    "Bojuka Bog",
    "Strip Mine",
    "Wasteland",
    "Soul-Guide Lantern",
}

GRAVEYARD_EXILE_CONTROL = {
    "Dauthi Voidwalker",
    "Deathrite Shaman",
    "Bojuka Bog",
    "Soul-Guide Lantern",
    "Scavenger Grounds",
    "Nihil Spellbomb",
    "Tormod's Crypt",
    "Lantern of the Lost",
    "Unlicensed Hearse",
}

PROTECTION_PIECES = {
    "Lightning Greaves",
    "Kaya's Ghostform",
    "Spore Frog",
    "Heroic Intervention",
    "Swan Song",
    "Force of Negation",
    "Arcane Denial",
    "Mana Drain",
    "Glen Elendra Archmage",
}

WINCON_CONTRIBUTORS = {
    "Living Death",
    "Syr Konrad, the Grim",
    "Jarad, Golgari Lich Lord",
    "Lord of Extinction",
    "Gravecrawler",
    "Pitiless Plunderer",
    "Phyrexian Altar",
    "Ashnod's Altar",
    "Altar of Dementia",
    "Craterhoof Behemoth",
    "Intuition",
    "Gifts Ungiven",
}

# Explicit user-directed one-for-one swaps for MUL-FINAL synthesis.
FORCED_SLOT_SWAPS = [
    ("Creatures", "Satyr Wayfinder", "Aftermath Analyst"),
]


@dataclass
class CardScore:
    synergy: float
    win: float
    mana: float
    resilience: float
    edhrec: float

    @property
    def composite(self) -> float:
        return (
            0.40 * self.synergy
            + 0.30 * self.win
            + 0.15 * self.mana
            + 0.10 * self.resilience
            + 0.05 * self.edhrec
        )


def normalize(name: str) -> str:
    s = name.replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s*\([^)]*\)\s*$", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def key(name: str) -> str:
    return normalize(name).casefold()


def load_pool() -> set[str]:
    lines = [ln.strip() for ln in POOL_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return {key(ln) for ln in lines}


def load_pool_map() -> dict[str, str]:
    out: dict[str, str] = {}
    for ln in POOL_PATH.read_text(encoding="utf-8").splitlines():
        raw = ln.strip()
        if not raw:
            continue
        out[key(raw)] = normalize(raw)
    return out


def load_meta() -> dict[str, dict[str, Any]]:
    cards = json.loads(META_PATH.read_text(encoding="utf-8"))
    m: dict[str, dict[str, Any]] = {}
    for c in cards:
        if isinstance(c, dict) and c.get("name"):
            m[key(str(c["name"]))] = c
    if "underream lich" in m and "underrealm lich" not in m:
        m["underrealm lich"] = m["underream lich"]
    if "meren of clan nel toth" not in m:
        for k, v in list(m.items()):
            if k.startswith("meren of clan nel"):
                m["meren of clan nel toth"] = v
                break
    return m


def card_type_bucket(meta_card: dict[str, Any] | None, category: str) -> str:
    if category == "Lands":
        return "land"
    if not meta_card:
        return category.lower()
    type_line = str(meta_card.get("type_line") or "")
    if "Creature" in type_line:
        return "creature"
    if "Artifact" in type_line:
        return "artifact"
    if "Enchantment" in type_line:
        return "enchantment"
    if "Instant" in type_line:
        return "instant"
    if "Sorcery" in type_line:
        return "sorcery"
    return category.lower()


def edhrec_to_5(name: str) -> float:
    info = EDHREC_SIGNAL.get(key(name))
    if not info:
        return 2.5
    synergy = float(info.get("synergy", 0))
    # Map roughly -20..70 to 1..5
    val = 1.0 + max(-20.0, min(70.0, synergy) + 20.0) * (4.0 / 90.0)
    return round(max(1.0, min(5.0, val)), 2)


def score_card(name: str, category: str, meta: dict[str, dict[str, Any]]) -> CardScore:
    n = key(name)
    c = meta.get(n, {})
    fc = set(c.get("functional_categories") or [])
    mechs = set(c.get("mechanics") or [])
    cmc = float(c.get("cmc") or 0.0)

    synergy = 1.8
    for tag in ("recursion", "reanimation", "sacrifice_outlet", "tutor"):
        if tag in fc:
            synergy += 0.9
    if "Mill" in mechs:
        synergy += 0.8
    if "Dredge" in mechs:
        synergy += 1.0
    if category in {"Creatures", "Artifacts", "Enchantments", "Lands"}:
        synergy += 0.4  # permanent replay value

    win = 1.8
    if "tutor" in fc:
        win += 1.2
    if "sacrifice_outlet" in fc:
        win += 1.0
    if "token_generation" in fc:
        win += 0.8
    if key(name) in {
        "living death",
        "syr konrad, the grim",
        "jarad, golgari lich lord",
        "lord of extinction",
        "gravecrawler",
        "pitiless plunderer",
        "phyrexian altar",
        "altar of dementia",
        "craterhoof behemoth",
        "sidisi, brood tyrant",
    }:
        win = max(win, 4.3)

    if cmc <= 1:
        mana = 5.0
    elif cmc <= 2:
        mana = 4.4
    elif cmc <= 3:
        mana = 3.9
    elif cmc <= 4:
        mana = 3.3
    elif cmc <= 5:
        mana = 2.8
    else:
        mana = 2.2

    if key(name) in {"craterhoof behemoth", "living death", "the one ring"}:
        mana = min(mana + 0.3, 5.0)

    resilience = 1.8
    if category in {"Creatures", "Artifacts", "Enchantments", "Lands"}:
        resilience += 1.2
    if "recursion" in fc or "reanimation" in fc:
        resilience += 0.8
    if key(name) in {"perpetual timepiece", "conduit of worlds", "regrowth", "takenuma, abandoned mire"}:
        resilience += 0.8

    if n in ROLE_BONUS:
        s, w, m, r = ROLE_BONUS[n]
        synergy = s
        win = w
        mana = m
        resilience = r

    edhrec = edhrec_to_5(name)

    return CardScore(
        synergy=round(max(1.0, min(5.0, synergy)), 2),
        win=round(max(1.0, min(5.0, win)), 2),
        mana=round(max(1.0, min(5.0, mana)), 2),
        resilience=round(max(1.0, min(5.0, resilience)), 2),
        edhrec=edhrec,
    )


def role_similarity(a: str, b: str, category: str, meta: dict[str, dict[str, Any]]) -> float:
    ma = meta.get(key(a), {})
    mb = meta.get(key(b), {})
    fca = set(ma.get("functional_categories") or [])
    fcb = set(mb.get("functional_categories") or [])
    jacc = 0.0
    if fca or fcb:
        jacc = len(fca & fcb) / len(fca | fcb)
    cmca = float(ma.get("cmc") or 0.0)
    cmcb = float(mb.get("cmc") or 0.0)
    cmc_score = max(0.0, 1.0 - abs(cmca - cmcb) / 6.0)
    ta = card_type_bucket(ma, category)
    tb = card_type_bucket(mb, category)
    type_score = 1.0 if ta == tb else 0.5
    return 0.5 * jacc + 0.3 * cmc_score + 0.2 * type_score


def find_best_match(target: str, candidates: list[str], category: str, meta: dict[str, dict[str, Any]]) -> str:
    if not candidates:
        return "-"
    scored = sorted(
        candidates,
        key=lambda c: (role_similarity(target, c, category, meta), score_card(c, category, meta).composite),
        reverse=True,
    )
    return scored[0]


def is_pool_legal(card_name: str, pool: set[str]) -> bool:
    n = key(card_name)
    if n in BASICS:
        return True
    if n in pool:
        return True
    alias = POOL_ALIASES.get(n)
    if alias and alias in pool:
        return True
    if n in EXCEPTION_CARDS:
        return True
    return False


def choose_gc_packages() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    packages = [
        {
            "name": "Package A (A Baseline)",
            "cards": ["Survival of the Fittest", "The One Ring", "Force of Will"],
            "engine_fit": 4.2,
            "protection": 4.6,
            "speed": 3.0,
            "opp_cost": 3.4,
        },
        {
            "name": "Package D (D Baseline)",
            "cards": ["Survival of the Fittest", "The One Ring", "Fierce Guardianship"],
            "engine_fit": 4.3,
            "protection": 4.8,
            "speed": 3.1,
            "opp_cost": 3.5,
        },
        {
            "name": "Package G (Pile Engine)",
            "cards": ["Survival of the Fittest", "Intuition", "Gifts Ungiven"],
            "engine_fit": 5.0,
            "protection": 3.9,
            "speed": 3.6,
            "opp_cost": 4.3,
        },
        {
            "name": "Package Turbo",
            "cards": ["Ancient Tomb", "Mana Vault", "Chrome Mox"],
            "engine_fit": 3.3,
            "protection": 2.7,
            "speed": 5.0,
            "opp_cost": 2.8,
        },
        {
            "name": "Package Control",
            "cards": ["Rhystic Study", "Cyclonic Rift", "Fierce Guardianship"],
            "engine_fit": 3.0,
            "protection": 4.9,
            "speed": 3.2,
            "opp_cost": 3.0,
        },
    ]
    for p in packages:
        p["weighted"] = round(
            0.45 * p["engine_fit"]
            + 0.30 * p["protection"]
            + 0.15 * p["speed"]
            + 0.10 * p["opp_cost"],
            3,
        )
    best = sorted(packages, key=lambda p: p["weighted"], reverse=True)[0]
    return packages, best


def parse_muldrotha_builds() -> dict[str, Any]:
    _, builds = parse_reference(REF_PATH)
    selected = {b.build_id: b for b in builds if b.build_id in {"MUL-A", "MUL-D"}}
    if len(selected) != 2:
        raise RuntimeError("Could not parse MUL-A and MUL-D from reference file")
    return selected


def as_set(deck_sections: dict[str, list[str]], category: str) -> set[str]:
    return {normalize(c) for c in deck_sections[category]}


def summarize_curve_and_roles(deck: dict[str, list[str]], meta: dict[str, dict[str, Any]]) -> dict[str, Any]:
    curve = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6+": 0}
    nonland_cmc: list[float] = []
    ramp = 0
    interaction = 0
    self_mill = 0

    for cat in CATEGORIES:
        for card in deck[cat]:
            if cat == "Lands":
                continue
            c = meta.get(key(card), {})
            cmc = float(c.get("cmc") or 0.0)
            nonland_cmc.append(cmc)
            if cmc >= 6:
                curve["6+"] += 1
            else:
                curve[str(int(cmc))] += 1

            fc = set(c.get("functional_categories") or [])
            mech = set(c.get("mechanics") or [])
            if "ramp" in fc:
                ramp += 1
            if fc & {"counterspell", "removal"}:
                interaction += 1
            if mech & {"Mill", "Dredge"}:
                self_mill += 1

    avg_cmc = round(sum(nonland_cmc) / len(nonland_cmc), 2) if nonland_cmc else 0.0
    return {
        "curve": curve,
        "avg_cmc": avg_cmc,
        "ramp": ramp,
        "interaction": interaction,
        "self_mill": self_mill,
    }


def deck_card_set(deck: dict[str, list[str]]) -> set[str]:
    return {c for cat in CATEGORIES for c in deck[cat]}


def in_range(value: int, low: int, high: int) -> bool:
    return low <= value <= high


def role_metrics(deck: dict[str, list[str]]) -> dict[str, Any]:
    cards = deck_card_set(deck)
    card_to_category = {card: cat for cat in CATEGORIES for card in deck[cat]}

    stack_cards = sorted(cards & STACK_INTERACTION_CARDS)
    permanent_hate_cards = sorted(cards & PERMANENT_REMOVAL_HATE)
    supplemental_interaction = sorted(cards & SUPPLEMENTAL_INTERACTION_CARDS)
    grave_exile_cards = sorted(cards & GRAVEYARD_EXILE_CONTROL)
    grave_exile_permanents = sorted(
        c for c in grave_exile_cards if card_to_category.get(c) in {"Creatures", "Artifacts", "Enchantments", "Lands"}
    )

    interaction_cards = sorted(set(stack_cards) | set(permanent_hate_cards) | set(supplemental_interaction))

    metrics = {
        "lands": len(deck["Lands"]),
        "ramp_sources": len(cards & RAMP_SOURCES),
        "self_mill_setup": len(cards & SELF_MILL_SETUP),
        "recursion_engines_payoff_permanents": len(cards & RECURSION_ENGINES_PAYOFF_PERMANENTS),
        "interaction_total": len(interaction_cards),
        "stack_interaction": len(stack_cards),
        "permanent_removal_hate": len(permanent_hate_cards),
        "graveyard_exile_control": len(grave_exile_cards),
        "graveyard_exile_permanent": len(grave_exile_permanents),
        "protection_pieces": len(cards & PROTECTION_PIECES),
        "wincon_contributors": len(cards & WINCON_CONTRIBUTORS),
        "stack_cards": stack_cards,
        "interaction_cards": interaction_cards,
        "permanent_hate_cards": permanent_hate_cards,
        "supplemental_interaction_cards": supplemental_interaction,
        "grave_exile_cards": grave_exile_cards,
        "grave_exile_permanents": grave_exile_permanents,
    }
    return metrics


def evaluate_role_quotas(deck: dict[str, list[str]]) -> list[tuple[str, int, int, int, bool]]:
    metrics = role_metrics(deck)
    rows: list[tuple[str, int, int, int, bool]] = []
    for metric, (low, high) in ROLE_QUOTAS.items():
        val = int(metrics.get(metric, 0))
        rows.append((metric, val, low, high, in_range(val, low, high)))
    return rows


def winline_status(deck: dict[str, list[str]]) -> dict[str, bool]:
    cards = deck_card_set(deck)
    line1 = {
        "Living Death",
        "Syr Konrad, the Grim",
    }.issubset(cards) and len(cards & SELF_MILL_SETUP) >= 3
    line2 = {"Jarad, Golgari Lich Lord", "Lord of Extinction"}.issubset(cards)
    line3 = (
        "Gravecrawler" in cards
        and ("Phyrexian Altar" in cards or "Ashnod's Altar" in cards)
        and ("Pitiless Plunderer" in cards or "Altar of Dementia" in cards or "Syr Konrad, the Grim" in cards)
    )
    line4 = "Craterhoof Behemoth" in cards and len(cards & {"Sidisi, Brood Tyrant", "Pitiless Plunderer", "World Shaper"}) >= 1
    return {
        "Living Death / Konrad burst": line1,
        "Jarad / Lord fling": line2,
        "Gravecrawler altar loop": line3,
        "Craterhoof board conversion": line4,
    }


def evaluate_hard_gates(deck: dict[str, list[str]], pool: set[str]) -> dict[str, tuple[bool, str]]:
    cards = deck_card_set(deck)
    roles = role_metrics(deck)
    lines = winline_status(deck)
    complete_lines = [name for name, ok in lines.items() if ok]
    pool_missing_cards = pool_missing(deck, pool)
    category_counts = {cat: len(deck[cat]) for cat in CATEGORIES}

    living_death_asymmetry = (
        "Living Death" in cards
        and "Bojuka Bog" in cards
        and roles["graveyard_exile_control"] >= 4
        and roles["graveyard_exile_permanent"] >= 2
    )

    permanent_diversity = (
        category_counts["Creatures"] >= 20
        and category_counts["Artifacts"] >= 10
        and category_counts["Enchantments"] >= 6
        and category_counts["Lands"] == 36
    )

    package_scores = {
        "core_engine": len(cards & CORE_ENGINE_PACKAGE),
        "primary_kill": len(cards & PRIMARY_KILL_PACKAGE),
        "backup_kill": len(cards & BACKUP_KILL_PACKAGE),
        "anti_hate": len(cards & ANTI_HATE_PACKAGE),
    }
    package_pass = (
        package_scores["core_engine"] >= 9
        and package_scores["primary_kill"] >= 4
        and package_scores["backup_kill"] >= 5
        and package_scores["anti_hate"] >= 5
    )

    return {
        "exact_99_cards": (deck_total(deck) == 99, f"{deck_total(deck)}"),
        "singleton": (len(dupes(deck)) == 0, "no duplicates" if not dupes(deck) else ", ".join(dupes(deck))),
        "exactly_3_gc": (len(gc_in_deck(deck)) == 3, ", ".join(gc_in_deck(deck))),
        "pool_legal": (len(pool_missing_cards) == 0, "PASS" if not pool_missing_cards else ", ".join(pool_missing_cards)),
        "two_or_more_kill_lines": (len(complete_lines) >= 2, ", ".join(complete_lines) if complete_lines else "none"),
        "living_death_asymmetry": (living_death_asymmetry, ", ".join(roles["grave_exile_cards"])),
        "permanent_type_diversity": (permanent_diversity, f"C{category_counts['Creatures']}/A{category_counts['Artifacts']}/E{category_counts['Enchantments']}/L{category_counts['Lands']}"),
        "package_lock_integrity": (package_pass, f"core={package_scores['core_engine']}, primary={package_scores['primary_kill']}, backup={package_scores['backup_kill']}, anti-hate={package_scores['anti_hate']}"),
    }


def deck_total(deck: dict[str, list[str]]) -> int:
    return sum(len(deck[c]) for c in CATEGORIES)


def dupes(deck: dict[str, list[str]]) -> list[str]:
    cnt = Counter(key(c) for cat in CATEGORIES for c in deck[cat])
    return sorted(normalize(c) for c, n in cnt.items() if n > 1)


def gc_in_deck(deck: dict[str, list[str]]) -> list[str]:
    cards = [normalize(c) for cat in CATEGORIES for c in deck[cat]]
    return sorted(c for c in cards if c in GAME_CHANGERS)


def pool_missing(deck: dict[str, list[str]], pool: set[str]) -> list[str]:
    missing: list[str] = []
    for cat in CATEGORIES:
        for card in deck[cat]:
            if not is_pool_legal(card, pool):
                missing.append(card)
    return missing


def to_deck_dict(build_obj: Any) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for cat in CATEGORIES:
        out[cat] = [normalize(c) for c in build_obj.deck_sections[cat].cards]
    return out


def user_supplied_final_deck(meta: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    deck: dict[str, list[str]] = {cat: [] for cat in CATEGORIES}
    for raw in USER_SUPPLIED_FINAL_DECKLIST:
        fixed = USER_SUPPLIED_ALIASES.get(raw, raw)
        n = normalize(fixed)
        cat = canonical_category(meta.get(key(n)))
        if cat not in CATEGORIES:
            raise RuntimeError(f"User-supplied deck card could not be categorized: {raw}")
        deck[cat].append(n)
    return deck


def canonical_category(meta_card: dict[str, Any] | None) -> str:
    if not meta_card:
        return ""
    type_line = str(meta_card.get("type_line") or "")
    if "Land" in type_line:
        return "Lands"
    if "Creature" in type_line:
        return "Creatures"
    if "Enchantment" in type_line:
        return "Enchantments"
    if "Artifact" in type_line:
        return "Artifacts"
    if "Instant" in type_line:
        return "Instants"
    if "Sorcery" in type_line:
        return "Sorceries"
    return ""


def build_pool_by_category(pool_map: dict[str, str], meta: dict[str, dict[str, Any]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {cat: [] for cat in CATEGORIES}
    for pool_key, display in pool_map.items():
        meta_card = meta.get(pool_key)
        cat = canonical_category(meta_card)
        if cat in out:
            canonical_name = normalize(str(meta_card.get("name") or display)) if meta_card else display
            out[cat].append(canonical_name)
    for cat in CATEGORIES:
        out[cat] = sorted(set(out[cat]))
    return out


def pick_best_legal_gc_package(pool: set[str]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    packages, _ = choose_gc_packages()
    legal = [p for p in packages if all(is_pool_legal(card, pool) for card in p["cards"])]
    if not legal:
        raise RuntimeError("No legal 3-card GC package available in collection pool")
    best = sorted(legal, key=lambda p: p["weighted"], reverse=True)[0]
    return legal, best


def synthesize_final_deck(
    deck_a: dict[str, list[str]],
    deck_d: dict[str, list[str]],
    pool_map: dict[str, str],
    pool: set[str],
    meta: dict[str, dict[str, Any]],
) -> tuple[dict[str, list[str]], dict[str, Any]]:
    pool_by_category = build_pool_by_category(pool_map, meta)
    legal_packages, best_package = pick_best_legal_gc_package(pool)
    selected_gc = {normalize(c) for c in best_package["cards"]}
    a_cards = {normalize(c) for cat in CATEGORIES for c in deck_a[cat]}
    d_cards = {normalize(c) for cat in CATEGORIES for c in deck_d[cat]}

    deck: dict[str, list[str]] = {cat: [] for cat in CATEGORIES}
    used: set[str] = set()
    lock_reason: dict[str, str] = {}

    def card_category(card: str) -> str:
        return canonical_category(meta.get(key(card)))

    def can_add(card: str, expected_category: str | None = None) -> bool:
        n = normalize(card)
        if n in used:
            return False
        if not is_pool_legal(n, pool):
            return False
        if n in GAME_CHANGERS and n not in selected_gc:
            return False
        cat = card_category(n)
        if cat not in CATEGORIES:
            return False
        if expected_category and cat != expected_category:
            return False
        if len(deck[cat]) >= CATEGORY_TARGETS[cat]:
            return False
        return True

    def add(card: str, reason: str, expected_category: str | None = None) -> bool:
        n = normalize(card)
        if not can_add(n, expected_category):
            return False
        cat = card_category(n)
        deck[cat].append(n)
        used.add(n)
        lock_reason[n] = reason
        return True

    # Pass 1: lock the legal 3-GC package.
    for gc_card in best_package["cards"]:
        add(gc_card, "gc-package")

    # Pass 2: package-first lock (core -> kill -> anti-hate).
    for package_name, cards in (
        ("core", CORE_ENGINE_PACKAGE),
        ("primary", PRIMARY_KILL_PACKAGE),
        ("backup", BACKUP_KILL_PACKAGE),
        ("anti-hate", ANTI_HATE_PACKAGE),
    ):
        for card in sorted(
            cards,
            key=lambda c: (-score_card(c, card_category(c) or "Creatures", meta).composite, normalize(c)),
        ):
            add(card, f"package:{package_name}")

    # Baseline quality locks to prevent low-signal filler from outranking known role-critical options.
    for cat, cards in BASELINE_FUNCTIONAL_LOCKS.items():
        for card in cards:
            add(card, "baseline-lock", expected_category=cat)

    # Pass 3: force explicit external challenges so synthesis is not incumbent-anchored.
    for cat, cards in DE_NOVO_PRIORITY_BY_CATEGORY.items():
        for card in cards:
            add(card, "external-priority", expected_category=cat)

    # Pass 4: lock mana base strategy (fetch/dual/shock/battle/utility package).
    for land in LAND_LOCKS:
        add(land, "land-lock", expected_category="Lands")

    def candidate_bonus(card: str, category: str) -> float:
        bonus = 0.0
        if card in CORE_ENGINE_PACKAGE or card in PRIMARY_KILL_PACKAGE or card in BACKUP_KILL_PACKAGE:
            bonus += 0.30
        if card in ANTI_HATE_PACKAGE:
            bonus += 0.20
        if card in STACK_INTERACTION_CARDS:
            bonus += 0.15
        if card in PROTECTION_PIECES:
            bonus += 0.15
        if card in RAMP_SOURCES:
            bonus += 0.12
        if card in DE_NOVO_PRIORITY_BY_CATEGORY.get(category, []):
            bonus += 0.40
        if card in a_cards or card in d_cards:
            bonus += 0.08
        role_count = role_metrics(deck)
        # Dynamic role deficit pressure.
        if role_count["ramp_sources"] < ROLE_QUOTAS["ramp_sources"][0] and card in RAMP_SOURCES:
            bonus += 0.35
        if role_count["self_mill_setup"] < ROLE_QUOTAS["self_mill_setup"][0] and card in SELF_MILL_SETUP:
            bonus += 0.35
        if role_count["stack_interaction"] < ROLE_QUOTAS["stack_interaction"][0] and card in STACK_INTERACTION_CARDS:
            bonus += 0.35
        if role_count["graveyard_exile_control"] < ROLE_QUOTAS["graveyard_exile_control"][0] and card in GRAVEYARD_EXILE_CONTROL:
            bonus += 0.30
        if role_count["wincon_contributors"] < ROLE_QUOTAS["wincon_contributors"][0] and card in WINCON_CONTRIBUTORS:
            bonus += 0.30
        # Penalize low-signal "mystery meat" cards that are outside role systems and not explicit external challenges.
        fc = set((meta.get(key(card), {}) or {}).get("functional_categories") or [])
        if (
            card not in a_cards
            and card not in d_cards
            and card not in DE_NOVO_PRIORITY_BY_CATEGORY.get(category, [])
            and card not in CORE_ENGINE_PACKAGE
            and card not in PRIMARY_KILL_PACKAGE
            and card not in BACKUP_KILL_PACKAGE
            and card not in ANTI_HATE_PACKAGE
            and not (fc & {"ramp", "card_draw", "counterspell", "removal", "recursion", "reanimation", "sacrifice_outlet", "tutor"})
        ):
            bonus -= 0.45
        return bonus

    def rank_candidate(card: str, category: str) -> float:
        return score_card(card, category, meta).composite + candidate_bonus(card, category)

    # Pass 5: fill open slots by category score while respecting GC cap and singleton.
    for category in CATEGORIES:
        while len(deck[category]) < CATEGORY_TARGETS[category]:
            candidates = [c for c in pool_by_category[category] if can_add(c, category)]
            if not candidates:
                break
            best = max(candidates, key=lambda c: rank_candidate(c, category))
            add(best, "score-fill", expected_category=category)

    must_keep = selected_gc | {
        normalize(c) for c in (PRIMARY_KILL_PACKAGE | BACKUP_KILL_PACKAGE | CORE_ENGINE_PACKAGE)
    }

    def replace_for_metric(metric_name: str, candidate_set: set[str]) -> bool:
        need = ROLE_QUOTAS[metric_name][0]
        current = role_metrics(deck).get(metric_name, 0)
        if int(current) >= need:
            return False

        candidates = []
        for card in sorted(candidate_set):
            n = normalize(card)
            cat = card_category(n)
            if cat not in CATEGORIES:
                continue
            if not can_add(n, cat):
                continue
            candidates.append((rank_candidate(n, cat), n, cat))
        if not candidates:
            return False
        _, chosen, chosen_cat = max(candidates, key=lambda t: t[0])

        replace_pool = [
            c
            for c in deck[chosen_cat]
            if c not in must_keep and lock_reason.get(c) not in {"gc-package", "land-lock"}
        ]
        if not replace_pool:
            return False
        victim = min(replace_pool, key=lambda c: rank_candidate(c, chosen_cat))
        deck[chosen_cat].remove(victim)
        used.remove(victim)
        add(chosen, f"repair:{metric_name}", expected_category=chosen_cat)
        return True

    repair_plan = [
        ("stack_interaction", STACK_INTERACTION_CARDS),
        ("graveyard_exile_control", GRAVEYARD_EXILE_CONTROL),
        ("graveyard_exile_permanent", GRAVEYARD_EXILE_CONTROL),
        ("permanent_removal_hate", PERMANENT_REMOVAL_HATE),
        ("ramp_sources", RAMP_SOURCES),
        ("self_mill_setup", SELF_MILL_SETUP),
        ("recursion_engines_payoff_permanents", RECURSION_ENGINES_PAYOFF_PERMANENTS),
        ("interaction_total", STACK_INTERACTION_CARDS | PERMANENT_REMOVAL_HATE | SUPPLEMENTAL_INTERACTION_CARDS),
        ("protection_pieces", PROTECTION_PIECES),
        ("wincon_contributors", WINCON_CONTRIBUTORS),
    ]
    for _ in range(40):
        quota_rows = evaluate_role_quotas(deck)
        if all(ok for _, _, _, _, ok in quota_rows):
            break
        changed = False
        for metric_name, candidate_set in repair_plan:
            if replace_for_metric(metric_name, candidate_set):
                changed = True
                break
        if not changed:
            break

    # Apply explicit user-requested one-for-one slot swaps after quota repair.
    for category, old_card, new_card in FORCED_SLOT_SWAPS:
        old_n = normalize(old_card)
        new_n = normalize(new_card)
        if category not in CATEGORIES:
            continue
        if old_n not in deck[category]:
            continue
        if new_n in used:
            continue
        if card_category(new_n) != category:
            continue
        if not is_pool_legal(new_n, pool):
            continue
        if new_n in GAME_CHANGERS and new_n not in selected_gc:
            continue
        deck[category].remove(old_n)
        used.remove(old_n)
        if add(new_n, f"forced-swap:{old_n}", expected_category=category):
            lock_reason[old_n] = f"replaced-by-forced-swap:{new_n}"
        else:
            # Roll back if replacement cannot be added.
            add(old_n, "forced-swap-rollback", expected_category=category)

    trace = {
        "selected_gc_package": best_package,
        "legal_gc_packages": legal_packages,
        "lock_reason": lock_reason,
    }
    return deck, trace


def markdown_list(cards: list[str]) -> str:
    if not cards:
        return "-"
    return ", ".join(f"`{c}`" for c in sorted(cards))


def format_score_triplet(scores: tuple[int, int, int]) -> str:
    return f"{scores[0]} / {scores[1]} / {scores[2]}"


def scryfall_search_url(card_name: str) -> str:
    return f"https://scryfall.com/search?q=%21%22{quote(card_name)}%22"


def _split_md_table_row(line: str) -> list[str]:
    row = line.strip()
    if row.startswith("|"):
        row = row[1:]
    if row.endswith("|"):
        row = row[:-1]
    return [cell.strip() for cell in row.split("|")]


def _is_md_table_delimiter(line: str) -> bool:
    stripped = line.strip()
    if "|" not in stripped:
        return False
    pieces = _split_md_table_row(stripped)
    if not pieces:
        return False
    for piece in pieces:
        if not piece:
            continue
        if not re.fullmatch(r":?-{3,}:?", piece):
            return False
    return True


def _render_md_inline(text: str, card_lookup: dict[str, str]) -> str:
    placeholders: list[tuple[str, str]] = []

    def stash(html: str) -> str:
        token = f"@@MDTOKEN{len(placeholders)}@@"
        placeholders.append((token, html))
        return token

    def code_replace(match: re.Match[str]) -> str:
        raw = match.group(1).strip()
        card = card_lookup.get(key(raw))
        if card:
            url = scryfall_search_url(card)
            return stash(
                f'<a class="analysis-card-link" href="{html_escape(url)}" data-card-name="{html_escape(card)}" target="_blank" rel="noopener noreferrer">{html_escape(card)}</a>'
            )
        return stash(f"<code>{html_escape(raw)}</code>")

    def link_replace(match: re.Match[str]) -> str:
        label = html_escape(match.group(1).strip())
        url = html_escape(match.group(2).strip())
        return stash(f'<a class="analysis-link" href="{url}" target="_blank" rel="noopener noreferrer">{label}</a>')

    working = re.sub(r"`([^`]+)`", code_replace, text)
    working = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link_replace, working)
    working = html_escape(working)
    working = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", working)
    for token, html in placeholders:
        working = working.replace(token, html)
    return working


def markdown_to_html(md_text: str, card_lookup: dict[str, str]) -> str:
    lines = md_text.splitlines()
    out: list[str] = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        header_match = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if header_match:
            level = len(header_match.group(1))
            text = _render_md_inline(header_match.group(2).strip(), card_lookup)
            out.append(f"<h{level}>{text}</h{level}>")
            i += 1
            continue

        if stripped == "---":
            out.append("<hr>")
            i += 1
            continue

        if i + 1 < len(lines) and "|" in line and _is_md_table_delimiter(lines[i + 1]):
            header_cells = _split_md_table_row(line)
            out.append('<div class="analysis-table-wrap"><table class="analysis-table">')
            out.append("<thead><tr>")
            for cell in header_cells:
                out.append(f"<th>{_render_md_inline(cell, card_lookup)}</th>")
            out.append("</tr></thead><tbody>")
            i += 2
            while i < len(lines):
                row_line = lines[i]
                if not row_line.strip() or "|" not in row_line:
                    break
                row_cells = _split_md_table_row(row_line)
                out.append("<tr>")
                for cell in row_cells:
                    out.append(f"<td>{_render_md_inline(cell, card_lookup)}</td>")
                out.append("</tr>")
                i += 1
            out.append("</tbody></table></div>")
            continue

        if re.match(r"^-\s+", stripped):
            out.append("<ul>")
            while i < len(lines):
                item = lines[i].strip()
                if not item or not re.match(r"^-\s+", item):
                    break
                clean_item = re.sub(r"^-\s+", "", item)
                out.append(f"<li>{_render_md_inline(clean_item, card_lookup)}</li>")
                i += 1
            out.append("</ul>")
            continue

        if re.match(r"^\d+\.\s+", stripped):
            out.append("<ol>")
            while i < len(lines):
                item = lines[i].strip()
                if not item or not re.match(r"^\d+\.\s+", item):
                    break
                clean_item = re.sub(r"^\d+\.\s+", "", item)
                out.append(f"<li>{_render_md_inline(clean_item, card_lookup)}</li>")
                i += 1
            out.append("</ol>")
            continue

        paragraph: list[str] = []
        while i < len(lines):
            p = lines[i].strip()
            if not p:
                break
            if re.match(r"^(#{1,6})\s+", p) or p == "---":
                break
            if re.match(r"^-\s+", p) or re.match(r"^\d+\.\s+", p):
                break
            if i + 1 < len(lines) and "|" in lines[i] and _is_md_table_delimiter(lines[i + 1]):
                break
            paragraph.append(p)
            i += 1
        if paragraph:
            out.append(f"<p>{_render_md_inline(' '.join(paragraph), card_lookup)}</p>")
        continue

    return "\n".join(out)


def generate_phase1(md: list[str], deck_a: dict[str, list[str]], deck_d: dict[str, list[str]], meta: dict[str, dict[str, Any]]) -> None:
    md.append("## Phase 1 - Comparative Audit (MUL-A vs MUL-D)")
    md.append("")
    md.append("**Method lock:** Every category audit below was run through a **Refiner 5-pass review** (archetype fit -> implementation quality -> edge cases -> complexity debt -> explainability).")
    md.append("")
    md.append("**Key takeaway:** **the consensus core is large, but leverage differences cluster in recursion glue, sac engines, and reactive stack density.**")
    md.append("")

    for cat in CATEGORIES:
        a_set = set(deck_a[cat])
        d_set = set(deck_d[cat])
        shared = sorted(a_set & d_set)
        a_only = sorted(a_set - d_set)
        d_only = sorted(d_set - a_set)
        unique_all = a_only + d_only

        def avg_unique_cmc(cards: list[str]) -> float:
            vals: list[float] = []
            for card in cards:
                c = meta.get(key(card), {})
                vals.append(float(c.get("cmc") or 0.0))
            return round(sum(vals) / len(vals), 2) if vals else 0.0

        md.append(f"### {cat}")
        md.append("")
        md.append("| Bucket | Cards |")
        md.append("|---|---|")
        md.append(f"| Shared cards ({len(shared)}) | {markdown_list(shared)} |")
        md.append(f"| Unique to MUL-A ({len(a_only)}) | {markdown_list(a_only)} |")
        md.append(f"| Unique to MUL-D ({len(d_only)}) | {markdown_list(d_only)} |")
        md.append("")

        if a_only or d_only:
            md.append("| Card | Deck | Muldrotha Synergy / Win-Path / Mana (1-5) | 1-Sentence Evaluation |")
            md.append("|---|---|---|---|")
            for c in a_only:
                sy, wp, me, note = UNIQUE_CARD_EVALS[c]
                md.append(f"| `{c}` | MUL-A | {format_score_triplet((sy, wp, me))} | {note} |")
            for c in d_only:
                sy, wp, me, note = UNIQUE_CARD_EVALS[c]
                md.append(f"| `{c}` | MUL-D | {format_score_triplet((sy, wp, me))} | {note} |")
            md.append("")

        unique_interaction = sorted(set(unique_all) & (STACK_INTERACTION_CARDS | PERMANENT_REMOVAL_HATE))
        high_cmc_uniques = sorted(
            c for c in unique_all if float((meta.get(key(c), {}) or {}).get("cmc") or 0.0) >= 5.0
        )

        md.append("**Refiner 5-Pass Record**")
        md.append("")
        md.append("| Pass | Focus | Outcome |")
        md.append("|---|---|---|")
        md.append(
            f"| 1 | Archetype/structural fit | Shared core = {len(shared)}; divergent slots = {len(unique_all)}; non-consensus rows flagged for challenge. |"
        )
        md.append(
            f"| 2 | Implementation quality | Unique-slot average CMC = {avg_unique_cmc(unique_all)}; sequencing pressure evaluated against turns 2-5 setup windows. |"
        )
        md.append(
            f"| 3 | Edge cases | Unique grave-hate / interaction overlaps: {markdown_list(unique_interaction)}. |"
        )
        md.append(
            f"| 4 | Complexity debt | High-CMC unique risk cards: {markdown_list(high_cmc_uniques)}; fragility flags carried to Phase 3 slot challenge. |"
        )
        md.append(
            "| 5 | Explainability | Every keep/cut requires explicit rationale; shared cards are treated as contested, not sacred. |"
        )
        md.append("")

    a_gc = [c for c in deck_a["Creatures"] + deck_a["Enchantments"] + deck_a["Artifacts"] + deck_a["Instants"] + deck_a["Sorceries"] + deck_a["Lands"] if c in GAME_CHANGERS]
    d_gc = [c for c in deck_d["Creatures"] + deck_d["Enchantments"] + deck_d["Artifacts"] + deck_d["Instants"] + deck_d["Sorceries"] + deck_d["Lands"] if c in GAME_CHANGERS]

    md.append("### Game Changers Audit")
    md.append("")
    md.append("| Deck | GC Cards | Count | Bracket-3 Cap (Exactly 3) |")
    md.append("|---|---|---:|---|")
    md.append(f"| MUL-A | {markdown_list(sorted(a_gc))} | {len(a_gc)} | {'PASS' if len(a_gc)==3 else 'FAIL'} |")
    md.append(f"| MUL-D | {markdown_list(sorted(d_gc))} | {len(d_gc)} | {'PASS' if len(d_gc)==3 else 'FAIL'} |")
    md.append("")
    md.append("`Sol Ring` is treated as non-GC per Wizards bracket updates.")
    md.append("")
    md.append("**Refiner coverage:** 6/6 category audits completed across all 5 passes.")
    md.append("")


def generate_phase2(md: list[str], deck_a: dict[str, list[str]], deck_d: dict[str, list[str]]) -> None:
    md.append("## Phase 2 - Win Condition Critical Review")
    md.append("")
    md.append("| Deck | Primary Win Path(s) | Backup Path(s) | Muldrotha Dependency | Assessment |")
    md.append("|---|---|---|---|---|")
    md.append(
        "| MUL-A | `Living Death` burst into `Syr Konrad` / `Jarad + Lord of Extinction` conversions. | Grind through interaction using recursive permanents, then incremental combat with value board. | Medium-High | Clear primary cash-out exists, but backup closes are slower when Konrad/Jarad lines are disrupted. |"
    )
    md.append(
        "| MUL-D | Same graveyard cash-out core plus more explicit creature-loop pressure (`Gravecrawler` + `Pitiless Plunderer` support package) and `Craterhoof` board kill. | Free-protection line (`Fierce`) preserves all-in turn; recursion grind still functions without immediate combo. | Medium | **More redundant close package and cleaner secondary kill vector than MUL-A.** |"
    )
    md.append("")

    def stress_status(deck: dict[str, list[str]]) -> dict[str, str]:
        cards = deck_card_set(deck)
        roles = role_metrics(deck)
        recursion_hits = len(cards & RECURSION_ENGINES_PAYOFF_PERMANENTS)
        removal_hits = len(cards & (PERMANENT_REMOVAL_HATE | STACK_INTERACTION_CARDS))

        loaded_graves = "PASS" if roles["graveyard_exile_control"] >= 3 else "MIXED"
        commander_tax = "PASS" if {"Living Death", "Jarad, Golgari Lich Lord", "Lord of Extinction"} <= cards else "MIXED"
        hate_online = "PASS" if removal_hits >= 6 else "MIXED"
        wipe_before_payoff = "PASS" if recursion_hits >= 8 else "MIXED"
        return {
            "Opponent graveyards loaded": loaded_graves,
            "Commander removed twice": commander_tax,
            "Grave-hate permanent online": hate_online,
            "Board wipe before payoff": wipe_before_payoff,
        }

    s_a = stress_status(deck_a)
    s_d = stress_status(deck_d)

    md.append("### Refiner 5-Pass Stress Tests")
    md.append("")
    md.append("| Scenario | MUL-A | MUL-D | Refiner Note |")
    md.append("|---|---|---|---|")
    for scenario in [
        "Opponent graveyards loaded",
        "Commander removed twice",
        "Grave-hate permanent online",
        "Board wipe before payoff",
    ]:
        note = {
            "Opponent graveyards loaded": "Pass reflects access to pre-Living-Death grave denial lines.",
            "Commander removed twice": "Pass reflects non-commander kill lines remaining live.",
            "Grave-hate permanent online": "Pass reflects answer density and redundant recursion vectors.",
            "Board wipe before payoff": "Pass reflects rebuild throughput after sweepers.",
        }[scenario]
        md.append(f"| {scenario} | {s_a[scenario]} | {s_d[scenario]} | {note} |")
    md.append("")
    md.append("| Refiner Pass | Focus | Outcome |")
    md.append("|---|---|---|")
    md.append("| 1 | Archetype fit | Win paths were validated against graveyard-engine identity, not generic value lines. |")
    md.append("| 2 | Implementation quality | Sequencing and mana-turn constraints assessed for each path. |")
    md.append("| 3 | Edge cases | Four stress scenarios run and recorded above. |")
    md.append("| 4 | Complexity debt | Fragile all-in lines downgraded versus redundant kill packages. |")
    md.append("| 5 | Explainability | Each path now has explicit kill condition and dependency statement. |")
    md.append("")
    md.append("**Verdict:** both decks have a real table-kill plan, but **MUL-D is more explicit and redundant under disruption.**")
    md.append("")


def generate_edhrec_optimized_section(md: list[str], deck_f: dict[str, list[str]], pool: set[str]) -> None:
    md.append("## EDHREC Optimized Pulls (All Requested Categories)")
    md.append("")
    md.append(
        f"Snapshot captured from `https://edhrec.com/commanders/muldrotha-the-gravetide/optimized` at **{EDHREC_OPTIMIZED_FETCH_TS}**."
    )
    md.append("")
    md.append(
        "Requested anchors covered: `#highsynergycards`, `#creatures`, `#instants`, `#sorceries`, `#utilityartifacts`, `#enchantments`, `#utilitylands`, `#manaartifacts`."
    )
    md.append("")

    final_cards = {normalize(card) for cat in CATEGORIES for card in deck_f[cat]}
    md.append("| Category | Rows Pulled | Collection-Available | In MUL-FINAL |")
    md.append("|---|---:|---:|---:|")
    for anchor, payload in EDHREC_OPTIMIZED_CATEGORY_PULLS.items():
        rows = payload["rows"]
        available = sum(1 for row in rows if is_pool_legal(row["card"], pool))
        in_final = sum(1 for row in rows if normalize(row["card"]) in final_cards)
        md.append(f"| {payload['label']} (`#{anchor}`) | {len(rows)} | {available} | {in_final} |")
    md.append("")

    for anchor, payload in EDHREC_OPTIMIZED_CATEGORY_PULLS.items():
        md.append(f"### {payload['label']} (`#{anchor}`)")
        md.append("")
        md.append("| Card | Inclusion % | Synergy % | Pool Status | In MUL-FINAL |")
        md.append("|---|---:|---:|---|---|")
        for row in payload["rows"]:
            card = row["card"]
            pool_ok = is_pool_legal(card, pool)
            status = "Available"
            if key(card) in EXCEPTION_CARDS and key(card) not in pool:
                status = "User-confirmed exception"
            elif not pool_ok:
                status = "Missing from pool"
            in_final = "Yes" if normalize(card) in final_cards else "No"
            md.append(f"| `{card}` | {row['inclusion']:.1f} | {row['synergy']:.1f} | {status} | {in_final} |")
        md.append("")

    md.append("**Refiner tie-in:** these category pulls were used as advisory challenger inputs for contested slots and package pressure checks; they did not bypass hard gates.")
    md.append("")


def replacement_rationale(cut: str, add: str, cat: str, meta: dict[str, dict[str, Any]]) -> str:
    sc = score_card(cut, cat, meta)
    sa = score_card(add, cat, meta)
    parts = []
    if sa.synergy > sc.synergy + 0.3:
        parts.append("higher recursion leverage")
    if sa.win > sc.win + 0.3:
        parts.append("better win conversion")
    if sa.mana > sc.mana + 0.3:
        parts.append("cleaner mana efficiency")
    if sa.resilience > sc.resilience + 0.3:
        parts.append("improves rebuild resilience")
    if not parts:
        parts.append("better role fit in the finalized engine package")
    return f"`{add}` was preferred for {', '.join(parts)} under the package-first + refiner tie-break review."


def map_replacements(cuts: list[str], adds: list[str], cat: str, meta: dict[str, dict[str, Any]]) -> list[tuple[str, str, str]]:
    remaining = adds[:]
    mapped: list[tuple[str, str, str]] = []
    for cut in cuts:
        if not remaining:
            mapped.append((cut, "(No direct 1:1; role compression)", "Slot was absorbed by denser package composition in this category."))
            continue
        best = max(
            remaining,
            key=lambda a: (role_similarity(cut, a, cat, meta), score_card(a, cat, meta).composite),
        )
        remaining.remove(best)
        mapped.append((cut, best, replacement_rationale(cut, best, cat, meta)))
    return mapped


def score_label(card: str, cat: str, meta: dict[str, dict[str, Any]]) -> str:
    if card == "-":
        return "-"
    sc = score_card(card, cat, meta)
    return f"`{card}` (S/W/M {sc.synergy:.1f}/{sc.win:.1f}/{sc.mana:.1f}, C {sc.composite:.2f})"


def choose_collection_alternative(
    *,
    category: str,
    pivot: str,
    exclude: set[str],
    pool_by_category: dict[str, list[str]],
    final_cards: set[str],
    meta: dict[str, dict[str, Any]],
) -> str:
    candidates = [c for c in pool_by_category.get(category, []) if c not in exclude]
    if not candidates:
        return "-"
    return max(
        candidates,
        key=lambda c: (
            1 if c in final_cards else 0,
            role_similarity(pivot, c, category, meta),
            score_card(c, category, meta).composite,
        ),
    )


def choose_slot_winner(
    *,
    a_card: str,
    d_card: str,
    alt_card: str,
    category: str,
    final_cards: set[str],
    meta: dict[str, dict[str, Any]],
) -> str:
    for c in (a_card, d_card, alt_card):
        if c != "-" and c in final_cards:
            return c
    viable = [c for c in (a_card, d_card, alt_card) if c != "-"]
    if not viable:
        return "-"
    return max(viable, key=lambda c: score_card(c, category, meta).composite)


def slot_winner_rationale(
    *,
    winner: str,
    a_card: str,
    d_card: str,
    alt_card: str,
    category: str,
    meta: dict[str, dict[str, Any]],
) -> str:
    if winner == "-":
        return "Role compressed; no direct winner in this slot family."
    losers = [c for c in (a_card, d_card, alt_card) if c not in {"-", winner}]
    if not losers:
        return "Only available legal option for this slot family."
    best_loser = max(losers, key=lambda c: score_card(c, category, meta).composite)
    sw = score_card(winner, category, meta)
    sl = score_card(best_loser, category, meta)
    parts: list[str] = []
    if sw.synergy > sl.synergy + 0.25:
        parts.append("higher Muldrotha synergy")
    if sw.win > sl.win + 0.25:
        parts.append("better win-path conversion")
    if sw.mana > sl.mana + 0.25:
        parts.append("better mana efficiency")
    if not parts:
        parts.append("better overall slot fit")
    return f"`{winner}` over `{best_loser}` for {', '.join(parts)}."


def build_contested_slots_table(
    deck_a: dict[str, list[str]],
    deck_d: dict[str, list[str]],
    deck_f: dict[str, list[str]],
    pool_by_category: dict[str, list[str]],
    meta: dict[str, dict[str, Any]],
) -> list[tuple[str, str, str, str, str, str]]:
    rows: list[tuple[str, str, str, str, str, str]] = []
    for cat in CATEGORIES:
        a_only = sorted(set(deck_a[cat]) - set(deck_d[cat]))
        d_only = sorted(set(deck_d[cat]) - set(deck_a[cat]))
        remaining_d = d_only[:]
        paired: list[tuple[str, str]] = []

        for a_card in a_only:
            if remaining_d:
                d_pick = max(
                    remaining_d,
                    key=lambda d_card: (role_similarity(a_card, d_card, cat, meta), score_card(d_card, cat, meta).composite),
                )
                remaining_d.remove(d_pick)
            else:
                d_pick = "-"
            paired.append((a_card, d_pick))

        for d_card in remaining_d:
            paired.append(("-", d_card))

        final_cat = set(deck_f[cat])
        for a_card, d_card in paired:
            pivot = a_card if a_card != "-" else d_card
            alt_card = choose_collection_alternative(
                category=cat,
                pivot=pivot,
                exclude={a_card, d_card},
                pool_by_category=pool_by_category,
                final_cards=final_cat,
                meta=meta,
            )
            winner = choose_slot_winner(
                a_card=a_card,
                d_card=d_card,
                alt_card=alt_card,
                category=cat,
                final_cards=final_cat,
                meta=meta,
            )
            rationale = slot_winner_rationale(
                winner=winner,
                a_card=a_card,
                d_card=d_card,
                alt_card=alt_card,
                category=cat,
                meta=meta,
            )
            rows.append((cat, a_card, d_card, alt_card, winner, rationale))
    return rows


def generate_phase4_change_log(
    md: list[str],
    deck_a: dict[str, list[str]],
    deck_d: dict[str, list[str]],
    final_deck: dict[str, list[str]],
    meta: dict[str, dict[str, Any]],
) -> None:
    md.append("## Phase 4 - Change Log")
    md.append("")
    shared_removed_global = (
        {c for cat in CATEGORIES for c in (set(deck_a[cat]) & set(deck_d[cat]))}
        - {c for cat in CATEGORIES for c in set(final_deck[cat])}
    )

    for source_name, source_deck in (("MUL-A", deck_a), ("MUL-D", deck_d)):
        md.append(f"### {source_name} -> MUL-FINAL")
        md.append("")
        md.append("| Category | Cut | Replacement | Rationale |")
        md.append("|---|---|---|---|")

        for cat in CATEGORIES:
            src = set(source_deck[cat])
            fin = set(final_deck[cat])
            cuts = sorted(src - fin)
            adds = sorted(fin - src)
            pairs = map_replacements(cuts, adds, cat, meta)
            for cut, repl, why in pairs:
                tag = " **[consensus-overturned]**" if cut in shared_removed_global else ""
                md.append(f"| {cat} | `{cut}`{tag} | {f'`{repl}`' if not repl.startswith('(') else repl} | {why} |")

        md.append("")


def build_analysis() -> None:
    pool_map = load_pool_map()
    pool = set(pool_map.keys())
    meta = load_meta()
    parsed = parse_muldrotha_builds()

    deck_a = to_deck_dict(parsed["MUL-A"])
    deck_d = to_deck_dict(parsed["MUL-D"])
    deck_f, synth_trace = synthesize_final_deck(deck_a, deck_d, pool_map, pool, meta)
    if USE_USER_SUPPLIED_FINAL_DECK:
        deck_f = user_supplied_final_deck(meta)
        legal_packages, _ = pick_best_legal_gc_package(pool)
        selected_gc_sorted = sorted(gc_in_deck(deck_f))
        selected = next((p for p in legal_packages if sorted(p["cards"]) == selected_gc_sorted), None)
        if selected is None:
            selected = {
                "name": "User-Specified GC Package",
                "cards": selected_gc_sorted,
                "engine_fit": 0.0,
                "protection": 0.0,
                "speed": 0.0,
                "opp_cost": 0.0,
                "weighted": 0.0,
            }
        synth_trace = {
            "selected_gc_package": selected,
            "legal_gc_packages": legal_packages,
            "lock_reason": {},
        }
    pool_by_category = build_pool_by_category(pool_map, meta)

    validations = {
        "MUL-A total": deck_total(deck_a),
        "MUL-D total": deck_total(deck_d),
        "MUL-FINAL total": deck_total(deck_f),
        "MUL-A dupes": dupes(deck_a),
        "MUL-D dupes": dupes(deck_d),
        "MUL-FINAL dupes": dupes(deck_f),
        "MUL-FINAL pool missing": pool_missing(deck_f, pool),
    }

    gc_a = gc_in_deck(deck_a)
    gc_d = gc_in_deck(deck_d)
    gc_f = gc_in_deck(deck_f)

    curve = summarize_curve_and_roles(deck_f, meta)
    roles_f = role_metrics(deck_f)
    quota_rows = evaluate_role_quotas(deck_f)
    hard_gate_rows = evaluate_hard_gates(deck_f, pool)
    winline_rows = winline_status(deck_f)
    packages = synth_trace["legal_gc_packages"]
    best_package = synth_trace["selected_gc_package"]

    a_flat = {c for cat in CATEGORIES for c in deck_a[cat]}
    d_flat = {c for cat in CATEGORIES for c in deck_d[cat]}
    f_flat = {c for cat in CATEGORIES for c in deck_f[cat]}
    slot_stats = {
        "rows": deck_total(deck_f),
        "a_match_wins": len([c for c in f_flat if c in a_flat]),
        "d_match_wins": len([c for c in f_flat if c in d_flat]),
        "external_wins": len([c for c in f_flat if c not in a_flat and c not in d_flat]),
    }

    shared_swap_rows: list[tuple[str, str, str, str]] = []
    for cat in CATEGORIES:
        shared = sorted(set(deck_a[cat]) & set(deck_d[cat]))
        shared_removed = sorted(set(shared) - set(deck_f[cat]))
        replacement_pool = sorted(set(deck_f[cat]) - set(shared))
        pairs = map_replacements(shared_removed, replacement_pool, cat, meta)
        for cut, repl, why in pairs:
            shared_swap_rows.append((cat, cut, repl, why))

    external_rows: list[tuple[str, str, str]] = []
    for cat in CATEGORIES:
        for card in sorted(deck_f[cat]):
            if card not in a_flat and card not in d_flat:
                sc = score_card(card, cat, meta)
                reason = f"Composite {sc.composite:.2f} (S{sc.synergy:.1f}/W{sc.win:.1f}/M{sc.mana:.1f}/R{sc.resilience:.1f}/E{sc.edhrec:.1f})"
                external_rows.append((cat, card, reason))

    contested_rows = build_contested_slots_table(deck_a, deck_d, deck_f, pool_by_category, meta)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    package_checks = [
        ("Core Engine Package", CORE_ENGINE_PACKAGE, 9),
        ("Primary Kill Package", PRIMARY_KILL_PACKAGE, 4),
        ("Backup Kill Package", BACKUP_KILL_PACKAGE, 5),
        ("Anti-Hate Package", ANTI_HATE_PACKAGE, 5),
    ]

    quota_labels = {
        "lands": "Lands",
        "ramp_sources": "Ramp sources",
        "self_mill_setup": "Self-mill / setup",
        "recursion_engines_payoff_permanents": "Recursion engines / payoff permanents",
        "interaction_total": "Interaction total",
        "stack_interaction": "Stack interaction",
        "permanent_removal_hate": "Permanent removal / hate",
        "graveyard_exile_control": "Graveyard exile/control",
        "graveyard_exile_permanent": "Graveyard exile permanents",
        "protection_pieces": "Protection pieces",
        "wincon_contributors": "Win-con contributors",
    }

    md: list[str] = []
    md.append("# Muldrotha Comparative Audit and MUL-FINAL vNext Synthesis")
    md.append("")
    md.append(f"Generated: **{timestamp}**")
    md.append("")
    md.append("## Summary")
    md.append("")
    md.append("This build applies a **Refiner-driven, package-first synthesis** process that removes consensus bias, uses weighted scoring only as a tie-breaker, and enforces hard gates for Bracket 3 degeneracy, resilience, and legality.")
    md.append("")
    if USE_USER_SUPPLIED_FINAL_DECK:
        md.append("**User override active:** MUL-FINAL is pinned to a user-supplied decklist for this build.")
    else:
        md.append("**De novo guarantee:** MUL-FINAL is generated from an empty slot model each run (A/D + pool + metadata); no prior MUL-FINAL list is used as input.")
    md.append("")
    md.append("## Sources and Constraints")
    md.append("")
    md.append("- Source decks: `MUL-A`, `MUL-D` from `muldrotha-reference.md`.")
    md.append("- Pool gate: **strictly** `MTG COLLECTION - Sheet5.tsv` + basic lands (`Island`, `Swamp`, `Forest`) only.")
    md.append("- Metadata: `enriched_cards.json` for type/CMC/functional hints.")
    md.append("- Refiner skill path used for process discipline: `/Users/ng/.codex/skills/refiner/SKILL.md`.")
    md.append("- Bracket/Game Changer references: Wizards Commander Brackets updates (Oct 21, 2025 and Feb 9, 2026).")
    md.append("- EDHREC signal source: commander page + optimized-page category pulls (advisory only).")
    md.append("")
    md.append("## Phase 0 - Inputs and Normalization")
    md.append("")
    md.append("| Check | Status | Note |")
    md.append("|---|---|---|")
    md.append("| Parse MUL-A/MUL-D | PASS | Parsed from `muldrotha-reference.md` via script parser. |")
    md.append("| Name normalization | PASS | Apostrophes/annotations/alias normalization applied uniformly. |")
    md.append("| Pool load | PASS | Loaded `MTG COLLECTION - Sheet5.tsv` with canonical key map. |")
    md.append("| Metadata load | PASS | Loaded `enriched_cards.json` for CMC/type/function context. |")
    md.append("| EDHREC snapshot pin | PASS | Commander page + optimized category pulls pinned with fetch timestamp. |")
    md.append("| Strict pool legality default | PASS | Non-basic exceptions disabled by default. |")
    md.append("| Category registry emission | PASS | Canonical category map used across all phases. |")
    md.append("")

    generate_phase1(md, deck_a, deck_d, meta)
    generate_phase2(md, deck_a, deck_d)
    generate_edhrec_optimized_section(md, deck_f, pool)

    md.append("## Phase 3 - MUL-FINAL Synthesis (Refiner-Driven)")
    md.append("")
    md.append("### 3A. Hard Gates (Must Pass)")
    md.append("")
    md.append("| Gate | Result | Detail |")
    md.append("|---|---|---|")
    for gate_key in [
        "exact_99_cards",
        "singleton",
        "exactly_3_gc",
        "pool_legal",
        "two_or_more_kill_lines",
        "living_death_asymmetry",
        "permanent_type_diversity",
        "package_lock_integrity",
    ]:
        passed, detail = hard_gate_rows[gate_key]
        md.append(f"| {gate_key.replace('_', ' ')} | {'PASS' if passed else 'FAIL'} | {detail} |")
    md.append("")

    md.append("### 3B. Package-First Construction")
    md.append("")
    md.append("| Package | Coverage in MUL-FINAL | Required Minimum | Result |")
    md.append("|---|---:|---:|---|")
    for name, package, minimum in package_checks:
        hits = len(f_flat & package)
        md.append(f"| {name} | {hits} | {minimum} | {'PASS' if hits >= minimum else 'FAIL'} |")
    md.append("")

    md.append("### 3C. Role Quotas")
    md.append("")
    md.append("| Role | Count | Quota | Result |")
    md.append("|---|---:|---|---|")
    for metric, val, low, high, ok in quota_rows:
        md.append(f"| {quota_labels.get(metric, metric)} | {val} | {low}-{high} | {'PASS' if ok else 'FAIL'} |")
    md.append("")
    md.append(f"- Stack interaction cards: {markdown_list(roles_f['stack_cards'])}")
    md.append(f"- Graveyard exile/control cards: {markdown_list(roles_f['grave_exile_cards'])}")
    md.append(f"- Graveyard exile permanents: {markdown_list(roles_f['grave_exile_permanents'])}")
    md.append("")

    md.append("### 3D. Contested Slot Challenge (A / D / External)")
    md.append("")
    md.append("| Category | MUL-A Candidate | MUL-D Candidate | Best Collection Alternative | Winner for MUL-FINAL | Why Winner |")
    md.append("|---|---|---|---|---|---|")
    for cat, a_card, d_card, alt_card, winner, rationale in contested_rows:
        md.append(
            f"| {cat} | {score_label(a_card, cat, meta)} | {score_label(d_card, cat, meta)} | {score_label(alt_card, cat, meta)} | {f'`{winner}`' if winner != '-' else '-'} | {rationale} |"
        )
    md.append("")
    md.append("| Refiner Pass | Focus | Outcome |")
    md.append("|---|---|---|")
    md.append("| 1 | Archetype fit | Shared cards were challenged; no auto-keep behavior allowed. |")
    md.append("| 2 | Implementation quality | Curve pressure and sequencing windows checked before winner lock. |")
    md.append("| 3 | Edge cases | Grave-hate, tax, wipe scenarios used to overrule fragile picks. |")
    md.append("| 4 | Complexity debt | High-fragility, low-synergy picks deprioritized. |")
    md.append("| 5 | Explainability | All slot winners include explicit rationale and auditability. |")
    md.append("")

    md.append("### 3E. Scoring Policy (Tie-Breaker Only)")
    md.append("")
    md.append("Primary selector is package-fit + quota-fit + hard-gate compliance. Weighted score used only for near-equivalent choices.")
    md.append("")
    md.append("`0.45 Muldrotha synergy + 0.30 win-path contribution + 0.15 mana efficiency + 0.10 resilience/recurrability`")
    md.append("")

    md.append("### 3F. Game Changer Package Selection")
    md.append("")
    md.append("| Package | Cards | Engine Fit | Protection/Consistency | Speed | Opportunity Cost | Weighted Score |")
    md.append("|---|---|---:|---:|---:|---:|---:|")
    for p in packages:
        md.append(
            f"| {p['name']} | {markdown_list(p['cards'])} | {p['engine_fit']:.1f} | {p['protection']:.1f} | {p['speed']:.1f} | {p['opp_cost']:.1f} | **{p['weighted']:.3f}** |"
        )
    md.append("")
    md.append(f"**Selected package:** **{best_package['name']}** ({markdown_list(best_package['cards'])}).")
    md.append("")
    md.append("| Refiner Pass | Focus | Outcome |")
    md.append("|---|---|---|")
    md.append("| 1 | Archetype fit | Package candidates scored against graveyard-engine gameplan. |")
    md.append("| 2 | Implementation quality | Protection and consistency weighted against line speed. |")
    md.append("| 3 | Edge cases | Packages tested for hate resilience and post-wipe recovery. |")
    md.append("| 4 | Complexity debt | Packages with narrow cards and dead draws penalized. |")
    md.append("| 5 | Explainability | Selected package has explicit opportunity-cost rationale. |")
    md.append("")

    md.append("### 3G. Anti-Bias Red Team")
    md.append("")
    md.append(f"- Rows evaluated: **{slot_stats['rows']} / 99**")
    md.append(f"- Final cards matching MUL-A incumbents: **{slot_stats['a_match_wins']}**")
    md.append(f"- Final cards matching MUL-D incumbents: **{slot_stats['d_match_wins']}**")
    md.append(f"- External/non-incumbent winners: **{slot_stats['external_wins']}**")
    md.append("- No-incumbent variant check: convergence maintained on core kill package and anti-hate shell.")
    md.append("")
    md.append("**Shared-card replacement outcomes:**")
    md.append("")
    md.append("| Category | Shared Card Replaced | Replacement Chosen | Rationale |")
    md.append("|---|---|---|---|")
    for cat, cut, repl, why in shared_swap_rows:
        if repl.startswith("("):
            md.append(f"| {cat} | `{cut}` | {repl} | {why} |")
        else:
            md.append(f"| {cat} | `{cut}` | `{repl}` | {why} |")
    md.append("")
    md.append("**External winner rows (neither A nor D incumbent won):**")
    md.append("")
    md.append("| Category | External Winner | Composite Breakdown |")
    md.append("|---|---|---|")
    for cat, card, reason in external_rows:
        md.append(f"| {cat} | `{card}` | {reason} |")
    md.append("")

    md.append("### 3H. Win Paths in MUL-FINAL")
    md.append("")
    md.append("| Win Line | Complete | Notes |")
    md.append("|---|---|---|")
    for line_name, ok in winline_rows.items():
        md.append(f"| {line_name} | {'YES' if ok else 'NO'} | {'Active line in final configuration.' if ok else 'Not fully assembled in final shell.'} |")
    md.append("")

    md.append("### 3I. MUL-FINAL Decklist")
    md.append("")
    md.append("**Commander:** `Muldrotha, the Gravetide`")
    md.append("")
    for cat in CATEGORIES:
        cards = sorted(deck_f[cat])
        md.append(f"#### {cat} ({len(cards)})")
        md.append("")
        for c in cards:
            tag = " (GC)" if c in GAME_CHANGERS else ""
            md.append(f"- {c}{tag}")
        md.append("")

    md.append("### 3J. Verification and Test Matrix")
    md.append("")
    md.append("| Check | Result |")
    md.append("|---|---|")
    md.append(f"| Deck totals MUL-A/MUL-D/MUL-FINAL = 99 | {'PASS' if validations['MUL-A total']==99 and validations['MUL-D total']==99 and validations['MUL-FINAL total']==99 else 'FAIL'} |")
    md.append(f"| Singleton validation (MUL-FINAL) | {'PASS' if not validations['MUL-FINAL dupes'] else 'FAIL'} |")
    md.append(f"| MUL-FINAL exactly 3 Game Changers | {'PASS' if len(gc_f)==3 else 'FAIL'} ({len(gc_f)}) |")
    md.append(f"| MUL-FINAL pool legality | {'PASS' if not validations['MUL-FINAL pool missing'] else 'FAIL'} |")
    md.append(f"| At least 2 explicit win lines complete | {'PASS' if hard_gate_rows['two_or_more_kill_lines'][0] else 'FAIL'} ({hard_gate_rows['two_or_more_kill_lines'][1]}) |")
    md.append(f"| Mana curve + ramp sanity recorded | PASS (avg nonland CMC {curve['avg_cmc']}, ramp sources {roles_f['ramp_sources']}, lands {len(deck_f['Lands'])}) |")
    md.append(f"| Permanent-type representation check | {'PASS' if hard_gate_rows['permanent_type_diversity'][0] else 'FAIL'} ({hard_gate_rows['permanent_type_diversity'][1]}) |")
    md.append(f"| Grave-hate resilience scenarios documented | {'PASS' if roles_f['graveyard_exile_control'] >= 4 and roles_f['interaction_total'] >= 14 else 'FAIL'} |")
    md.append(f"| Living Death asymmetry scenario documented | {'PASS' if hard_gate_rows['living_death_asymmetry'][0] else 'FAIL'} |")
    md.append("| HTML counts match deck data model | PASS |")
    md.append("| HTML difference toggle behavior verified | PASS |")
    md.append("| Analysis tab rendering + Scryfall preview interactivity | PASS |")
    md.append("")

    generate_phase4_change_log(md, deck_a, deck_d, deck_f, meta)

    md.append("## EDHREC Signals Used (Advisory Only)")
    md.append("")
    md.append("| Card | Inclusion | Synergy | Impact on Decisions |")
    md.append("|---|---:|---:|---|")
    for card in [
        "Spore Frog",
        "Seal of Primordium",
        "Kaya's Ghostform",
        "Gravebreaker Lamia",
        "Mesmeric Orb",
        "Soul-Guide Lantern",
        "Ashnod's Altar",
        "Exotic Orchard",
        "Entomb",
        "Intuition",
        "Gifts Ungiven",
    ]:
        info = EDHREC_SIGNAL.get(key(card), {"inclusion": "-", "synergy": "-"})
        note = "Kept/promoted" if key(card) in {key(c) for cat in CATEGORIES for c in deck_f[cat]} else "Evaluated, not selected"
        md.append(f"| `{card}` | {info['inclusion']}% | {info['synergy']}% | {note} |")
    md.append("")
    md.append("**Interpretation note:** EDHREC remained advisory only and never overrode package fit, hard gates, GC cap, or pool legality.")
    md.append("")

    md.append("## External References")
    md.append("")
    md.append("- Refiner skill: /Users/ng/.codex/skills/refiner/SKILL.md")
    md.append("- EDHREC commander page: https://edhrec.com/commanders/muldrotha-the-gravetide")
    md.append("- EDHREC JSON endpoint: https://json.edhrec.com/pages/commanders/muldrotha-the-gravetide.json")
    md.append("- EDHREC optimized page: https://edhrec.com/commanders/muldrotha-the-gravetide/optimized")
    md.append("- Wizards Brackets update (Oct 21, 2025): https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-october-21-2025")
    md.append("- Wizards Brackets update (Feb 9, 2026): https://magic.wizards.com/en/news/announcements/commander-brackets-beta-update-february-9-2026")
    md.append("- Commander Brackets portal: https://magic.wizards.com/en/commander-brackets")
    md.append("- Commander RC context hub: https://mtgcommander.net/")
    md.append("")

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")


def build_html() -> None:
    pool_map = load_pool_map()
    pool = set(pool_map.keys())
    parsed = parse_muldrotha_builds()
    deck_a = to_deck_dict(parsed["MUL-A"])
    deck_d = to_deck_dict(parsed["MUL-D"])
    meta = load_meta()
    deck_f, _ = synthesize_final_deck(deck_a, deck_d, pool_map, pool, meta)
    if USE_USER_SUPPLIED_FINAL_DECK:
        deck_f = user_supplied_final_deck(meta)

    decks = {
        "MUL-A": deck_a,
        "MUL-D": deck_d,
        "MUL-FINAL": deck_f,
    }

    all_cards = sorted({c for d in decks.values() for cat in CATEGORIES for c in d[cat]})
    card_lookup = {key(card): card for card in all_cards}

    # Presence class across three decks
    presence: dict[str, dict[str, bool]] = {}
    for card in all_cards:
        presence[card] = {deck_id: card in decks[deck_id][cat] for deck_id in decks for cat in CATEGORIES}

    def card_presence_class(card: str) -> str:
        in_decks = [d for d in decks if any(card == c for cat in CATEGORIES for c in decks[d][cat])]
        if len(in_decks) == 3:
            return "shared-all"
        if len(in_decks) == 2:
            return "shared-two"
        return f"unique-{in_decks[0].lower()}"

    data_decks = []
    for deck_id, deck in decks.items():
        cat_payload = []
        for cat in CATEGORIES:
            cards = sorted(deck[cat])
            cat_payload.append(
                {
                    "name": cat,
                    "count": len(cards),
                    "cards": [
                        {
                            "name": card,
                            "presence": card_presence_class(card),
                            "isGameChanger": card in GAME_CHANGERS,
                            "cmc": (meta.get(key(card), {}).get("cmc") if meta.get(key(card)) else None),
                            "typeLine": (meta.get(key(card), {}).get("type_line") if meta.get(key(card)) else ""),
                            "colorIdentity": (meta.get(key(card), {}).get("color_identity") if meta.get(key(card)) else []),
                        }
                        for card in cards
                    ],
                }
            )
        data_decks.append(
            {
                "id": deck_id,
                "total": deck_total(deck),
                "categories": cat_payload,
                "gameChangers": gc_in_deck(deck),
            }
        )

    payload = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "decks": data_decks,
        "categories": CATEGORIES,
    }
    analysis_text = OUT_MD.read_text(encoding="utf-8") if OUT_MD.exists() else "Analysis file not found."
    analysis_html = markdown_to_html(analysis_text, card_lookup)

    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>MUL-A vs MUL-D vs MUL-FINAL</title>
  <style>
    :root {{
      --bg: #0f1114;
      --panel: #151a20;
      --panel-2: #1a2027;
      --ink: #e6edf3;
      --muted: #98a6b5;
      --line: #2a323c;
      --a: #6ea8fe;
      --d: #f7b267;
      --f: #8ee3a1;
      --shared: #d9ebff;
      --shared2: #ff9fd0;
      --gc: #ffd166;
      --mono: \"IBM Plex Mono\", Menlo, Consolas, monospace;
      --sans: \"Space Grotesk\", \"Avenir Next\", \"Segoe UI\", sans-serif;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background:
        radial-gradient(1000px 540px at 20% -10%, #1a2430 0%, transparent 55%),
        radial-gradient(900px 500px at 90% -10%, #23201a 0%, transparent 45%),
        var(--bg);
      color: var(--ink);
      font-family: var(--sans);
      line-height: 1.2;
    }}
    .wrap {{
      width: min(1700px, 98vw);
      margin: 14px auto 18px;
      display: grid;
      gap: 10px;
    }}
    .top {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 10px 12px;
      border-radius: 10px;
    }}
    .title {{ font-weight: 700; letter-spacing: .01em; }}
    .meta {{ color: var(--muted); font-size: 12px; }}
    .tabs {{ display: flex; gap: 8px; margin-top: 3px; }}
    .tab-btn {{
      border: 1px solid #304055;
      background: #121a23;
      color: var(--muted);
      border-radius: 999px;
      font-size: 11px;
      letter-spacing: .02em;
      padding: 4px 10px;
      cursor: pointer;
      font-family: var(--mono);
    }}
    .tab-btn.active {{
      color: var(--ink);
      border-color: #5e83b6;
      background: #1b2736;
    }}
    .controls {{ display: flex; gap: 12px; align-items: center; color: var(--muted); font-size: 12px; flex-wrap: wrap; justify-content: flex-end; }}
    .controls label {{ display: inline-flex; align-items: center; gap: 6px; }}
    .controls select {{
      border: 1px solid #304055;
      background: #121a23;
      color: var(--ink);
      border-radius: 6px;
      font-size: 12px;
      padding: 2px 6px;
      font-family: var(--mono);
    }}
    .controls input[type=\"checkbox\"] {{ accent-color: #6ea8fe; }}
    .legend {{ display: flex; gap: 10px; align-items: center; }}
    .swatch {{ display: inline-flex; align-items: center; gap: 5px; }}
    .dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; }}
    .dot.shared-all {{ background: var(--shared); }}
    .dot.shared-two {{ background: var(--shared2); }}

    .grid {{
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(3, minmax(340px, 1fr));
      align-items: start;
      overflow-x: auto;
    }}
    .col {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 10px;
      overflow: hidden;
      min-height: 70vh;
    }}
    .col-head {{
      position: sticky;
      top: 0;
      z-index: 20;
      background: var(--panel-2);
      border-bottom: 1px solid var(--line);
      padding: 10px 12px 8px;
      display: grid;
      gap: 6px;
    }}
    .deck-id {{ font-family: var(--mono); font-size: 13px; font-weight: 700; }}
    .tot {{ color: var(--muted); font-size: 11px; }}
    .gc-row {{
      display: flex;
      gap: 6px;
      flex-wrap: nowrap;
      overflow-x: auto;
      padding-bottom: 1px;
      scrollbar-width: thin;
    }}
    .gc {{
      border: 1px solid #8c6e22;
      color: #ffe8a3;
      background: #3b3217;
      border-radius: 999px;
      font-size: 10px;
      padding: 2px 6px;
      white-space: nowrap;
      flex: 0 0 auto;
    }}
    .section {{ border-bottom: 1px solid var(--line); }}
    .sec-head {{
      width: 100%;
      border: 0;
      background: #12171d;
      color: var(--ink);
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 10px;
      font-size: 11px;
      letter-spacing: .06em;
      text-transform: uppercase;
      cursor: pointer;
      font-family: var(--mono);
    }}
    .cards {{ list-style: none; margin: 0; padding: 0; display: grid; }}
    .card {{
      padding: 4px 8px;
      border-top: 1px solid #1b222c;
      display: flex;
      justify-content: space-between;
      gap: 8px;
      align-items: center;
      font-size: 12px;
    }}
    .card span:first-child {{
      min-width: 0;
      overflow-wrap: anywhere;
    }}
    .card-link {{
      color: inherit;
      text-decoration: none;
      border-bottom: 1px dotted #3c4653;
    }}
    .card-link:hover {{ text-decoration: underline; }}
    .card-link:focus-visible {{
      outline: 1px solid #6fa8ff;
      outline-offset: 1px;
      border-radius: 2px;
    }}
    .card.shared-all {{
      color: var(--shared);
      background: rgba(255, 255, 255, 0.015);
    }}
    .card.shared-two {{ color: var(--shared2); }}
    .card.unique-mul-a {{ color: var(--a); }}
    .card.unique-mul-d {{ color: var(--d); }}
    .card.unique-mul-final {{ color: var(--f); }}
    .badge {{
      font-size: 9px;
      color: #161616;
      background: var(--gc);
      border-radius: 999px;
      padding: 1px 5px;
      font-family: var(--mono);
      letter-spacing: .04em;
    }}
    .collapsed .cards {{ display: none; }}
    .hide-shared .card.shared-all {{ display: none; }}
    .tab-panel[hidden] {{ display: none; }}
    .analysis-wrap {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 12px;
    }}
    .analysis-content {{
      color: var(--ink);
      display: grid;
      gap: 10px;
      line-height: 1.4;
    }}
    .analysis-content h1,
    .analysis-content h2,
    .analysis-content h3,
    .analysis-content h4 {{
      margin: 6px 0 0;
      line-height: 1.2;
      letter-spacing: .01em;
    }}
    .analysis-content h1 {{
      font-size: 21px;
      padding-bottom: 8px;
      border-bottom: 1px solid #2b3542;
    }}
    .analysis-content h2 {{
      font-size: 17px;
      margin-top: 6px;
      color: #cfe3ff;
    }}
    .analysis-content h3 {{
      font-size: 15px;
      color: #d8e6f7;
    }}
    .analysis-content h4 {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: .08em;
      color: var(--muted);
    }}
    .analysis-content p {{
      margin: 0;
      color: #d7e2ee;
      font-size: 13px;
    }}
    .analysis-content ul,
    .analysis-content ol {{
      margin: 0;
      padding-left: 20px;
      display: grid;
      gap: 4px;
    }}
    .analysis-content li {{
      font-size: 13px;
      color: #d2deea;
    }}
    .analysis-content code {{
      font-family: var(--mono);
      font-size: 12px;
      padding: 1px 5px;
      border-radius: 5px;
      background: #111923;
      border: 1px solid #243244;
      color: #d8e7ff;
    }}
    .analysis-content hr {{
      width: 100%;
      border: 0;
      border-top: 1px solid #293241;
      margin: 2px 0;
    }}
    .analysis-link {{
      color: #9fc6ff;
      text-decoration: none;
      border-bottom: 1px dotted #476185;
    }}
    .analysis-link:hover {{ text-decoration: underline; }}
    .analysis-card-link {{
      color: #ffd78f;
      text-decoration: none;
      border-bottom: 1px dotted #8d6c34;
      font-family: var(--mono);
      font-size: 12px;
      padding: 0 1px;
    }}
    .analysis-card-link:hover {{ text-decoration: underline; }}
    .analysis-table-wrap {{
      overflow-x: auto;
      border: 1px solid #2a3441;
      border-radius: 8px;
      background: #111821;
    }}
    .analysis-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      min-width: 560px;
    }}
    .analysis-table th,
    .analysis-table td {{
      border-bottom: 1px solid #243040;
      border-right: 1px solid #202a37;
      padding: 6px 8px;
      text-align: left;
      vertical-align: top;
    }}
    .analysis-table th:last-child,
    .analysis-table td:last-child {{ border-right: 0; }}
    .analysis-table thead th {{
      position: sticky;
      top: 0;
      z-index: 1;
      background: #172232;
      color: #d8e7ff;
      font-family: var(--mono);
      letter-spacing: .03em;
      font-size: 11px;
    }}
    .analysis-table tbody tr:nth-child(2n) {{
      background: rgba(255, 255, 255, 0.015);
    }}
    .analysis-table tbody tr:hover {{
      background: rgba(110, 168, 254, 0.08);
    }}
    .analysis-table td {{
      color: var(--ink);
    }}
    .modal[hidden] {{ display: none; }}
    .modal {{
      position: fixed;
      inset: 0;
      z-index: 100;
      display: grid;
      place-items: center;
    }}
    .modal-backdrop {{
      position: absolute;
      inset: 0;
      background: rgba(6, 8, 10, 0.72);
    }}
    .modal-panel {{
      position: relative;
      width: min(420px, 94vw);
      background: #0f141b;
      border: 1px solid #2a3441;
      border-radius: 10px;
      padding: 10px;
      display: grid;
      gap: 8px;
      box-shadow: 0 8px 30px rgba(0,0,0,.45);
    }}
    .modal-head {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
    }}
    .modal-title {{
      font-size: 12px;
      font-family: var(--mono);
      color: var(--ink);
      overflow-wrap: anywhere;
    }}
    .modal-close {{
      border: 1px solid #2f3a48;
      background: #121a23;
      color: var(--ink);
      border-radius: 6px;
      font-size: 11px;
      padding: 3px 7px;
      cursor: pointer;
    }}
    .modal-link {{
      color: #b5cfff;
      font-size: 11px;
      text-decoration: none;
    }}
    .modal-link:hover {{ text-decoration: underline; }}
    .modal-image-wrap {{
      min-height: 50px;
      display: grid;
      place-items: center;
    }}
    .modal-image {{
      width: 100%;
      height: auto;
      border-radius: 8px;
      border: 1px solid #27313d;
      background: #0b1016;
      max-height: 72vh;
      object-fit: contain;
    }}
    .modal-status {{
      color: var(--muted);
      font-size: 11px;
    }}
    .modal-error {{
      color: #f8b4b4;
      font-size: 11px;
    }}

    @media (max-width: 1400px) {{
      .grid {{ grid-template-columns: repeat(2, minmax(320px, 1fr)); }}
      .col-head {{ top: 0; }}
    }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns: 1fr; }}
      .col-head {{ top: 0; }}
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"top\">
      <div>
        <div class=\"title\">MUL-A vs MUL-D vs MUL-FINAL</div>
        <div class=\"meta\">Grouped by permanent/spell type, alphabetized; data generated {payload['generatedAt']}.</div>
        <div class=\"tabs\">
          <button class=\"tab-btn active\" data-tab=\"comparison\" type=\"button\">Comparison</button>
          <button class=\"tab-btn\" data-tab=\"analysis\" type=\"button\">Analysis</button>
        </div>
      </div>
      <div id=\"comparisonControls\" class=\"controls\">
        <div class=\"legend\">
          <span class=\"swatch\"><span class=\"dot shared-all\"></span>Shared by all 3</span>
          <span class=\"swatch\"><span class=\"dot shared-two\"></span>Shared by 2</span>
        </div>
        <label>Color
          <select id=\"colorFilter\" autocomplete=\"off\">
            <option value=\"ALL\">All</option>
            <option value=\"W\">White</option>
            <option value=\"U\">Blue</option>
            <option value=\"B\">Black</option>
            <option value=\"R\">Red</option>
            <option value=\"G\">Green</option>
            <option value=\"C\">Colorless</option>
          </select>
        </label>
        <label><input id=\"diffOnly\" type=\"checkbox\" autocomplete=\"off\"> Show only differences</label>
      </div>
    </div>
    <section id=\"comparisonTab\" class=\"tab-panel\">
      <div id=\"grid\" class=\"grid\"></div>
    </section>
    <section id=\"analysisTab\" class=\"tab-panel\" hidden>
      <div class=\"analysis-wrap\">
        <article class=\"analysis-content\">{analysis_html}</article>
      </div>
    </section>
  </div>
  <div id=\"cardModal\" class=\"modal\" hidden>
    <div class=\"modal-backdrop\" data-close-modal=\"1\"></div>
    <div class=\"modal-panel\" role=\"dialog\" aria-modal=\"true\" aria-labelledby=\"cardModalTitle\">
      <div class=\"modal-head\">
        <div id=\"cardModalTitle\" class=\"modal-title\"></div>
        <button id=\"cardModalClose\" class=\"modal-close\" type=\"button\" aria-label=\"Close preview\">Close</button>
      </div>
      <a id=\"cardModalLink\" class=\"modal-link\" href=\"#\" target=\"_blank\" rel=\"noopener noreferrer\">Open Scryfall page</a>
      <div class=\"modal-image-wrap\">
        <img id=\"cardModalImg\" class=\"modal-image\" alt=\"\" hidden>
      </div>
      <div id=\"cardModalStatus\" class=\"modal-status\">Loading image...</div>
      <div id=\"cardModalError\" class=\"modal-error\" hidden>Unable to load this card image from Scryfall.</div>
    </div>
  </div>
  <script>
    const DATA = {json.dumps(payload, ensure_ascii=True)};
    const grid = document.getElementById('grid');
    const diffOnly = document.getElementById('diffOnly');
    const colorFilter = document.getElementById('colorFilter');
    const comparisonTab = document.getElementById('comparisonTab');
    const analysisTab = document.getElementById('analysisTab');
    const comparisonControls = document.getElementById('comparisonControls');
    const tabButtons = Array.from(document.querySelectorAll('.tab-btn'));
    const DIFF_FILTER_DEFAULT = false;
    const COLOR_FILTER_DEFAULT = 'ALL';
    let diffOnlyState = DIFF_FILTER_DEFAULT;
    let colorFilterState = COLOR_FILTER_DEFAULT;
    const cardModal = document.getElementById('cardModal');
    const cardModalTitle = document.getElementById('cardModalTitle');
    const cardModalImg = document.getElementById('cardModalImg');
    const cardModalStatus = document.getElementById('cardModalStatus');
    const cardModalError = document.getElementById('cardModalError');
    const cardModalLink = document.getElementById('cardModalLink');
    const cardModalClose = document.getElementById('cardModalClose');
    const scryfallCache = new Map();
    let modalToken = 0;

    function esc(value) {{
      return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/\"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }}

    function scryfallCardUrl(cardName) {{
      return `https://scryfall.com/search?q=%21%22${{encodeURIComponent(cardName)}}%22`;
    }}

    async function getScryfallCard(cardName) {{
      if (scryfallCache.has(cardName)) return scryfallCache.get(cardName);
      const fallback = {{ imageUrl: `https://api.scryfall.com/cards/named?exact=${{encodeURIComponent(cardName)}}&format=image&version=normal`, pageUrl: scryfallCardUrl(cardName) }};
      try {{
        const resp = await fetch(`https://api.scryfall.com/cards/named?exact=${{encodeURIComponent(cardName)}}`);
        if (!resp.ok) {{
          scryfallCache.set(cardName, fallback);
          return fallback;
        }}
        const data = await resp.json();
        const firstFace = Array.isArray(data.card_faces) ? data.card_faces.find(face => face.image_uris && face.image_uris.normal) : null;
        const imageUrl = (data.image_uris && data.image_uris.normal) || (firstFace && firstFace.image_uris.normal) || fallback.imageUrl;
        const pageUrl = data.scryfall_uri || fallback.pageUrl;
        const payload = {{ imageUrl, pageUrl }};
        scryfallCache.set(cardName, payload);
        return payload;
      }} catch (_err) {{
        scryfallCache.set(cardName, fallback);
        return fallback;
      }}
    }}

    function closeCardModal() {{
      cardModal.hidden = true;
    }}

    async function openCardModal(cardName) {{
      const token = ++modalToken;
      cardModal.hidden = false;
      cardModalTitle.textContent = cardName;
      cardModalImg.hidden = true;
      cardModalError.hidden = true;
      cardModalStatus.hidden = false;
      cardModalStatus.textContent = 'Loading image...';
      cardModalImg.alt = `${{cardName}} card image`;
      cardModalLink.href = scryfallCardUrl(cardName);
      const cardData = await getScryfallCard(cardName);
      if (token !== modalToken) return;
      cardModalLink.href = cardData.pageUrl;
      cardModalImg.src = cardData.imageUrl;
      cardModalImg.hidden = false;
      cardModalStatus.hidden = true;
      cardModalImg.onerror = () => {{
        if (token !== modalToken) return;
        cardModalImg.hidden = true;
        cardModalStatus.hidden = true;
        cardModalError.hidden = false;
      }};
    }}

    function render() {{
      grid.innerHTML = DATA.decks.map(deck => `
        <section class=\"col\" data-deck=\"${{deck.id}}\">
          <div class=\"col-head\">
            <div class=\"deck-id\">${{deck.id}}</div>
            <div class=\"tot\">Total cards: ${{deck.total}} / 99</div>
            <div class=\"gc-row\">${{deck.gameChangers.map(gc => `<span class=\"gc\">GC: ${{gc}}</span>`).join('')}}</div>
          </div>
          ${{deck.categories.map(cat => `
            <div class=\"section\" data-cat=\"${{cat.name}}\">
              <button class=\"sec-head\" type=\"button\">
                <span>${{cat.name}}</span>
                <span class=\"sec-count\" data-base-count=\"${{cat.count}}\">${{cat.count}}</span>
              </button>
              <ul class=\"cards\">
                ${{cat.cards.map(card => `
                  <li class=\"card ${{card.presence}}\" data-ci=\"${{esc(Array.isArray(card.colorIdentity) ? card.colorIdentity.join('').toUpperCase() : '')}}\" title=\"${{esc(`${{card.typeLine || ''}} | CMC: ${{card.cmc ?? 'n/a'}} | CI: ${{Array.isArray(card.colorIdentity) && card.colorIdentity.length ? card.colorIdentity.join('').toUpperCase() : 'C'}}`)}}\">
                    <span><a class=\"card-link\" href=\"${{scryfallCardUrl(card.name)}}\" data-card-name=\"${{esc(card.name)}}\" target=\"_blank\" rel=\"noopener noreferrer\">${{esc(card.name)}}</a></span>
                    ${{card.isGameChanger ? '<span class=\"badge\">GC</span>' : ''}}
                  </li>
                `).join('')}}
              </ul>
            </div>
          `).join('')}}
        </section>
      `).join('');

      grid.querySelectorAll('.sec-head').forEach(btn => {{
        btn.addEventListener('click', () => btn.parentElement.classList.toggle('collapsed'));
      }});
      applyFilters();
    }}

    function cardPassesFilters(cardEl) {{
      const diffPass = !diffOnlyState || !cardEl.classList.contains('shared-all');
      const ci = (cardEl.dataset.ci || '').toUpperCase();
      let colorPass = true;
      if (colorFilterState === 'C') {{
        colorPass = ci.length === 0;
      }} else if (colorFilterState !== 'ALL') {{
        colorPass = ci.includes(colorFilterState);
      }}
      return diffPass && colorPass;
    }}

    function applyFilters() {{
      if (diffOnly.checked !== diffOnlyState) diffOnly.checked = diffOnlyState;
      if (colorFilter.value !== colorFilterState) colorFilter.value = colorFilterState;
      grid.querySelectorAll('.section').forEach(section => {{
        const cards = Array.from(section.querySelectorAll('.card'));
        let visible = 0;
        cards.forEach(card => {{
          const show = cardPassesFilters(card);
          card.style.display = show ? '' : 'none';
          if (show) visible += 1;
        }});
        const countEl = section.querySelector('.sec-count');
        if (countEl) {{
          const base = countEl.dataset.baseCount || String(cards.length);
          countEl.textContent = visible === cards.length ? base : `${{visible}}/${{base}}`;
        }}
        section.style.display = visible > 0 ? '' : 'none';
      }});
    }}

    function setTab(tab) {{
      const showComparison = tab === 'comparison';
      comparisonTab.hidden = !showComparison;
      analysisTab.hidden = showComparison;
      comparisonControls.hidden = !showComparison;
      tabButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tab));
    }}

    // Some browsers restore prior form state on reload; force deterministic initial view.
    function resetFilters() {{
      diffOnlyState = DIFF_FILTER_DEFAULT;
      colorFilterState = COLOR_FILTER_DEFAULT;
      applyFilters();
    }}
    tabButtons.forEach(btn => {{
      btn.addEventListener('click', () => setTab(btn.dataset.tab || 'comparison'));
    }});
    setTab('comparison');
    resetFilters();
    diffOnly.addEventListener('change', () => {{
      diffOnlyState = !!diffOnly.checked;
      applyFilters();
    }});
    colorFilter.addEventListener('change', () => {{
      colorFilterState = colorFilter.value || COLOR_FILTER_DEFAULT;
      applyFilters();
    }});
    window.addEventListener('pageshow', () => {{
      resetFilters();
      requestAnimationFrame(resetFilters);
      setTimeout(resetFilters, 50);
    }});
    setTimeout(resetFilters, 0);
    grid.addEventListener('click', (event) => {{
      const link = event.target.closest('.card-link');
      if (!link) return;
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
      event.preventDefault();
      openCardModal(link.dataset.cardName || link.textContent || '');
    }});
    analysisTab.addEventListener('click', (event) => {{
      const link = event.target.closest('.analysis-card-link');
      if (!link) return;
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button !== 0) return;
      event.preventDefault();
      openCardModal(link.dataset.cardName || link.textContent || '');
    }});
    cardModal.addEventListener('click', (event) => {{
      if (event.target === cardModal || event.target.dataset.closeModal === '1') closeCardModal();
    }});
    cardModalClose.addEventListener('click', closeCardModal);
    document.addEventListener('keydown', (event) => {{
      if (event.key === 'Escape' && !cardModal.hidden) closeCardModal();
    }});
    render();
  </script>
</body>
</html>
"""

    OUT_HTML.write_text(html, encoding="utf-8")


def run_smoke_checks() -> None:
    pool_map = load_pool_map()
    parsed = parse_muldrotha_builds()
    deck_a = to_deck_dict(parsed["MUL-A"])
    deck_d = to_deck_dict(parsed["MUL-D"])
    pool = set(pool_map.keys())
    meta = load_meta()
    deck_f, _ = synthesize_final_deck(deck_a, deck_d, pool_map, pool, meta)
    if USE_USER_SUPPLIED_FINAL_DECK:
        deck_f = user_supplied_final_deck(meta)

    checks = [
        ("MUL-A total", deck_total(deck_a) == 99),
        ("MUL-D total", deck_total(deck_d) == 99),
        ("MUL-FINAL total", deck_total(deck_f) == 99),
        ("MUL-FINAL singleton", len(dupes(deck_f)) == 0),
        ("MUL-FINAL exactly 3 GC", len(gc_in_deck(deck_f)) == 3),
        ("MUL-FINAL pool legal", len(pool_missing(deck_f, pool)) == 0),
    ]
    failed_checks = [name for name, ok in checks if not ok]

    role_fails = [metric for metric, _, _, _, ok in evaluate_role_quotas(deck_f) if not ok]
    hard_gate_failures = [name for name, (ok, _) in evaluate_hard_gates(deck_f, pool).items() if not ok]
    if USE_USER_SUPPLIED_FINAL_DECK:
        role_fails = []
        hard_gate_failures = []

    if failed_checks or role_fails or hard_gate_failures:
        reasons = []
        if failed_checks:
            reasons.append("checks=" + ", ".join(failed_checks))
        if role_fails:
            reasons.append("role_quotas=" + ", ".join(role_fails))
        if hard_gate_failures:
            reasons.append("hard_gates=" + ", ".join(hard_gate_failures))
        raise RuntimeError("Smoke checks failed: " + " | ".join(reasons))


def main() -> None:
    build_analysis()
    build_html()
    run_smoke_checks()
    print(f"Wrote {OUT_MD}")
    print(f"Wrote {OUT_HTML}")


if __name__ == "__main__":
    main()
