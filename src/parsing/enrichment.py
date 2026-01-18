"""Orchestrate card data enrichment."""

from .functional_roles import FunctionalRoleParser
from .mechanics import MechanicExtractor
from .properties import PropertyCalculator


def enrich_card_data(cards: list[dict]) -> list[dict]:
    """Add derived properties to all cards."""

    role_parser = FunctionalRoleParser()
    mechanic_extractor = MechanicExtractor()
    property_calc = PropertyCalculator()

    enriched = []

    print("Enriching card data...")
    for i, card in enumerate(cards):
        # Functional roles
        card["functional_categories"] = role_parser.identify_roles(
            card.get("oracle_text", "")
        )

        # Mechanics
        card["mechanics"] = mechanic_extractor.extract_mechanics(card)

        # Derived properties
        card["mana_efficiency"] = property_calc.calculate_mana_efficiency(card)
        card["color_pip_intensity"] = property_calc.count_color_pips(
            card.get("mana_cost", "")
        )
        card["is_fast_mana"] = property_calc.is_fast_mana(card)
        card["is_free_spell"] = property_calc.is_free_spell(card)

        enriched.append(card)

        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"  Processed {i + 1}/{len(cards)} cards...")

    print(f"✓ Enriched {len(enriched)} cards")
    return enriched
