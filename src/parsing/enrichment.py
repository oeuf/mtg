"""Orchestrate card data enrichment."""

from .functional_roles import FunctionalRoleParser
from .mechanics import MechanicExtractor
from .properties import PropertyCalculator
from .zone_detector import ZoneDetector
from .phase_detector import PhaseDetector
from .theme_detector import ThemeDetector


def enrich_card_data(cards: list[dict]) -> list[dict]:
    """Add derived properties to all cards."""

    role_parser = FunctionalRoleParser()
    mechanic_extractor = MechanicExtractor()
    property_calc = PropertyCalculator()
    zone_detector = ZoneDetector()
    phase_detector = PhaseDetector()
    theme_detector = ThemeDetector()

    enriched = []

    print("Enriching card data...")
    for i, card in enumerate(cards):
        oracle_text = card.get("oracle_text", "")
        type_line = card.get("type_line", "")

        # Functional roles
        card["functional_categories"] = role_parser.identify_roles(oracle_text)

        # Mechanics
        card["mechanics"] = mechanic_extractor.extract_mechanics(card)

        # Derived properties
        card["mana_efficiency"] = property_calc.calculate_mana_efficiency(card)
        card["color_pip_intensity"] = property_calc.count_color_pips(
            card.get("mana_cost", "")
        )
        card["is_fast_mana"] = property_calc.is_fast_mana(card)
        card["is_free_spell"] = property_calc.is_free_spell(card)

        # Subtypes (NEW)
        card["subtypes"] = property_calc.extract_subtypes(type_line)

        # Zone interactions
        zones = zone_detector.detect_zones(oracle_text)
        card["zone_interactions"] = [
            {"zone": zone, "interaction_type": data["interaction_type"]}
            for zone, data in zones.items()
        ]

        # Phase triggers
        phases = phase_detector.detect_phases(oracle_text)
        card["phase_triggers"] = [
            {"phase": phase, "trigger_type": data["trigger_type"]}
            for phase, data in phases.items()
        ]

        # Themes (NEW) - must run after mechanics/roles/zones
        card["themes"] = theme_detector.detect_themes(card)

        enriched.append(card)

        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(cards)} cards...")

    print(f"✓ Enriched {len(enriched)} cards")
    return enriched
