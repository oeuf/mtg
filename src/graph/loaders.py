"""Load cards and relationships into Neo4j graph."""

from .connection import Neo4jConnection


# Theme definitions
THEME_DEFINITIONS = {
    "reanimation": {
        "description": "Return creatures from graveyard to battlefield"
    },
    "aristocrats": {
        "description": "Sacrifice creatures for value and death triggers"
    },
    "tokens": {
        "description": "Create and benefit from creature tokens"
    },
    "lands_matter": {
        "description": "Landfall, ramp, and land recursion strategies"
    },
    "spellslinger": {
        "description": "Cast triggers and instant/sorcery synergies"
    },
    "graveyard_value": {
        "description": "Benefit from cards in graveyard"
    },
    "lifegain": {
        "description": "Gain life and benefit from lifegain triggers"
    },
    "tribal": {
        "description": "Creature type synergies"
    },
    "voltron": {
        "description": "Equipment, auras, and commander damage"
    },
    "stax": {
        "description": "Resource denial and tax effects"
    }
}


def load_card_to_graph(conn: Neo4jConnection, card_data: dict):
    """Create Card or Commander node in graph."""

    # Determine node label
    is_commander = (
        card_data.get("is_legendary") and
        card_data.get("can_be_commander")
    )

    node_label = "Commander" if is_commander else "Card"

    query = f"""
    MERGE (c:{node_label} {{name: $name}})
    SET c.mana_cost = $mana_cost,
        c.cmc = $cmc,
        c.type_line = $type_line,
        c.oracle_text = $oracle_text,
        c.color_identity = $color_identity,
        c.colors = $colors,
        c.keywords = $keywords,
        c.is_legendary = $is_legendary,
        c.is_reserved_list = $is_reserved_list,
        c.edhrec_rank = $edhrec_rank,
        c.functional_categories = $functional_categories,
        c.mechanics = $mechanics,
        c.mana_efficiency = $mana_efficiency,
        c.color_pip_intensity = $color_pip_intensity,
        c.is_free_spell = $is_free_spell,
        c.is_fast_mana = $is_fast_mana,
        c.subtypes = $subtypes,
        c.themes = $themes,
        c.archetype = $archetype
    """

    # For commanders, add additional properties
    if is_commander:
        query += """,
        c.can_be_commander = $can_be_commander
        """

    params = {
        "name": card_data["name"],
        "mana_cost": card_data.get("mana_cost", ""),
        "cmc": card_data.get("cmc", 0),
        "type_line": card_data.get("type_line", ""),
        "oracle_text": card_data.get("oracle_text", ""),
        "color_identity": card_data.get("color_identity", []),
        "colors": card_data.get("colors", []),
        "keywords": card_data.get("keywords", []),
        "is_legendary": card_data.get("is_legendary", False),
        "is_reserved_list": card_data.get("is_reserved_list", False),
        "edhrec_rank": card_data.get("edhrec_rank"),
        "functional_categories": card_data.get("functional_categories", []),
        "mechanics": card_data.get("mechanics", []),
        "mana_efficiency": card_data.get("mana_efficiency", 0.0),
        "color_pip_intensity": card_data.get("color_pip_intensity", 0),
        "is_free_spell": card_data.get("is_free_spell", False),
        "is_fast_mana": card_data.get("is_fast_mana", False),
        "can_be_commander": card_data.get("can_be_commander", False),
        "subtypes": card_data.get("subtypes", []),
        "themes": card_data.get("themes", []),
        "archetype": card_data.get("archetype", "utility"),
    }

    conn.execute_query(query, params)


def batch_load_cards(conn: Neo4jConnection, cards: list[dict]):
    """Load all cards in batches for performance."""

    batch_size = 100
    total = len(cards)

    print(f"Loading {total} cards into graph...")

    for i in range(0, total, batch_size):
        batch = cards[i:i+batch_size]

        for card in batch:
            load_card_to_graph(conn, card)

        if (i + batch_size) % 1000 == 0:
            print(f"  Loaded {min(i + batch_size, total)}/{total} cards...")

    print(f"✓ Loaded {total} cards")


def create_mechanic_relationships(conn: Neo4jConnection, card_data: dict):
    """Create [:HAS_MECHANIC] relationships."""

    card_name = card_data["name"]
    mechanics = card_data.get("mechanics", [])

    for i, mechanic in enumerate(mechanics):
        # Create mechanic node if doesn't exist
        query_mechanic = """
        MERGE (m:Mechanic {name: $mechanic_name})
        """
        conn.execute_query(query_mechanic, {"mechanic_name": mechanic})

        # Create relationship
        query_rel = """
        MATCH (c:Card {name: $card_name})
        MATCH (m:Mechanic {name: $mechanic_name})
        MERGE (c)-[:HAS_MECHANIC {is_primary: $is_primary}]->(m)
        """

        # First mechanic is primary
        is_primary = (i == 0)

        conn.execute_query(query_rel, {
            "card_name": card_name,
            "mechanic_name": mechanic,
            "is_primary": is_primary
        })


def create_role_relationships(conn: Neo4jConnection, card_data: dict):
    """Create [:FILLS_ROLE] relationships."""

    card_name = card_data["name"]
    roles = card_data.get("functional_categories", [])
    oracle_text = card_data.get("oracle_text", "").lower()

    for role in roles:
        # Create role node if doesn't exist
        query_role = """
        MERGE (r:Functional_Role {name: $role_name})
        """
        conn.execute_query(query_role, {"role_name": role})

        # Determine conditionality
        conditionality = "unconditional"
        if any(word in oracle_text for word in ["if", "when", "whenever", "as long as"]):
            conditionality = "conditional"
        if any(word in oracle_text for word in ["unless", "only if", "may"]):
            conditionality = "restrictive"

        # Create relationship
        query_rel = """
        MATCH (c:Card {name: $card_name})
        MATCH (r:Functional_Role {name: $role_name})
        MERGE (c)-[:FILLS_ROLE {
            efficiency_score: $efficiency,
            conditionality: $conditionality
        }]->(r)
        """

        conn.execute_query(query_rel, {
            "card_name": card_name,
            "role_name": role,
            "efficiency": card_data.get("mana_efficiency", 0.5),
            "conditionality": conditionality
        })


def create_related_card_relationships(conn: Neo4jConnection,
                                      card_name: str,
                                      related_data: dict):
    """Create relationships from MTGJSON RelatedCards.json."""

    if not related_data:
        return

    # 1. SPELLBOOK: Explicit combos/synergies
    spellbook = related_data.get("spellbook", [])
    for related_card in spellbook:
        query = """
        MATCH (c1:Card {name: $card_name})
        MATCH (c2:Card {name: $related_card})
        MERGE (c1)-[:COMBOS_WITH {
            source: "mtgjson_spellbook",
            confidence: 1.0
        }]->(c2)
        """

        try:
            conn.execute_query(query, {
                "card_name": card_name,
                "related_card": related_card
            })
        except Exception:
            # Related card might not be Commander-legal
            pass

    # 2. TOKENS: Token generation
    tokens = related_data.get("tokens", [])
    for token_name in tokens:
        # Create token node
        query_token = """
        MERGE (t:Token {name: $token_name})
        """
        conn.execute_query(query_token, {"token_name": token_name})

        # Create relationship
        query_rel = """
        MATCH (c:Card {name: $card_name})
        MATCH (t:Token {name: $token_name})
        MERGE (c)-[:CREATES_TOKEN {
            source: "mtgjson_related_cards"
        }]->(t)
        """

        conn.execute_query(query_rel, {
            "card_name": card_name,
            "token_name": token_name
        })

    # 3. REVERSE RELATED: Community pairings
    reverse_related = related_data.get("reverseRelated", [])
    for related_card in reverse_related:
        query = """
        MATCH (c1:Card {name: $card_name})
        MATCH (c2:Card {name: $related_card})
        MERGE (c1)-[:COMMONLY_PAIRED_WITH {
            source: "mtgjson_reverse_related"
        }]->(c2)
        """

        try:
            conn.execute_query(query, {
                "card_name": card_name,
                "related_card": related_card
            })
        except Exception:
            pass


def integrate_related_cards(conn: Neo4jConnection,
                           related_cards_data: dict):
    """Integrate all RelatedCards.json data into graph."""

    total = len(related_cards_data)
    processed = 0

    print(f"Integrating RelatedCards for {total} cards...")

    for card_name, relationships in related_cards_data.items():
        create_related_card_relationships(conn, card_name, relationships)
        processed += 1

        if processed % 1000 == 0:
            print(f"  Processed {processed}/{total}...")

    print(f"✓ Integrated {processed} card relationships")


def create_zone_nodes(conn: Neo4jConnection, zones: dict):
    """
    Create Zone nodes from rules parser data.

    Args:
        conn: Neo4j connection
        zones: Dict from rules parser with zone data
    """
    print(f"Creating {len(zones)} zone nodes...")

    for zone_name, zone_data in zones.items():
        query = """
        MERGE (z:Zone {name: $name})
        SET z.rule_number = $rule_number,
            z.is_public = $is_public,
            z.is_ordered = $is_ordered,
            z.description = $description
        """

        conn.execute_query(query, {
            "name": zone_name,
            "rule_number": zone_data["rule_number"],
            "is_public": zone_data["is_public"],
            "is_ordered": zone_data["is_ordered"],
            "description": zone_data.get("description", "")
        })

    print(f"✓ Created {len(zones)} zone nodes")


def create_phase_nodes(conn: Neo4jConnection, phases: dict):
    """
    Create Phase nodes from rules parser data.

    Args:
        conn: Neo4j connection
        phases: Dict from rules parser with phase data
    """
    print(f"Creating {len(phases)} phase nodes...")

    for phase_name, phase_data in phases.items():
        query = """
        MERGE (p:Phase {name: $name})
        SET p.rule_number = $rule_number,
            p.order = $order,
            p.parent = $parent,
            p.is_step = $is_step
        """

        conn.execute_query(query, {
            "name": phase_name,
            "rule_number": phase_data["rule_number"],
            "order": phase_data["order"],
            "parent": phase_data.get("parent"),
            "is_step": phase_data["is_step"]
        })

    print(f"✓ Created {len(phases)} phase nodes")


def create_zone_relationships(conn: Neo4jConnection, card_data: dict):
    """
    Create [:INTERACTS_WITH_ZONE] relationships for a card.

    Args:
        conn: Neo4j connection
        card_data: Card dict with zone_interactions list
    """
    card_name = card_data["name"]
    zone_interactions = card_data.get("zone_interactions", [])

    for interaction in zone_interactions:
        query = """
        MATCH (c:Card {name: $card_name})
        MATCH (z:Zone {name: $zone_name})
        MERGE (c)-[:INTERACTS_WITH_ZONE {
            interaction_type: $interaction_type
        }]->(z)
        """

        conn.execute_query(query, {
            "card_name": card_name,
            "zone_name": interaction["zone"],
            "interaction_type": interaction["interaction_type"]
        })


def create_phase_relationships(conn: Neo4jConnection, card_data: dict):
    """
    Create [:TRIGGERS_IN_PHASE] relationships for a card.

    Args:
        conn: Neo4j connection
        card_data: Card dict with phase_triggers list
    """
    card_name = card_data["name"]
    phase_triggers = card_data.get("phase_triggers", [])

    for trigger in phase_triggers:
        query = """
        MATCH (c:Card {name: $card_name})
        MATCH (p:Phase {name: $phase_name})
        MERGE (c)-[:TRIGGERS_IN_PHASE {
            trigger_type: $trigger_type
        }]->(p)
        """

        conn.execute_query(query, {
            "card_name": card_name,
            "phase_name": trigger["phase"],
            "trigger_type": trigger["trigger_type"]
        })


def create_theme_nodes(conn: Neo4jConnection, themes: dict):
    """
    Create Theme nodes from theme definitions.

    Args:
        conn: Neo4j connection
        themes: Dict mapping theme name to metadata
                Example: {"reanimation": {"description": "..."}}
    """
    print(f"Creating {len(themes)} theme nodes...")

    for theme_name, metadata in themes.items():
        query = """
        MERGE (t:Theme {name: $name})
        SET t.description = $description
        """

        conn.execute_query(query, {
            "name": theme_name,
            "description": metadata.get("description", "")
        })

    print(f"✓ Created {len(themes)} theme nodes")


def create_theme_relationships(conn: Neo4jConnection, card_data: dict):
    """
    Create [:SUPPORTS_THEME] relationships for a card.

    Args:
        conn: Neo4j connection
        card_data: Card dict with themes list
    """
    card_name = card_data["name"]
    themes = card_data.get("themes", [])

    for theme in themes:
        query = """
        MATCH (c:Card {name: $card_name})
        MATCH (t:Theme {name: $theme_name})
        MERGE (c)-[:SUPPORTS_THEME]->(t)
        """

        conn.execute_query(query, {
            "card_name": card_name,
            "theme_name": theme
        })


def batch_create_theme_relationships(conn: Neo4jConnection, cards: list[dict]):
    """
    Create theme relationships for all cards.

    Args:
        conn: Neo4j connection
        cards: List of card dicts with themes
    """
    total = len(cards)
    processed = 0

    print(f"Creating theme relationships for {total} cards...")

    for card in cards:
        if card.get("themes"):  # Only process cards with themes
            create_theme_relationships(conn, card)
        processed += 1

        if processed % 1000 == 0:
            print(f"  Processed {processed}/{total}...")

    print(f"✓ Created theme relationships for {processed} cards")


def create_subtype_relationships(conn: Neo4jConnection, card_data: dict):
    """
    Create [:HAS_SUBTYPE] relationships for a card.

    Args:
        conn: Neo4j connection
        card_data: Card dict with subtypes list
    """
    card_name = card_data["name"]
    subtypes = card_data.get("subtypes", [])

    for subtype in subtypes:
        # Create subtype node if doesn't exist
        query_subtype = """
        MERGE (s:Subtype {name: $subtype_name})
        """
        conn.execute_query(query_subtype, {"subtype_name": subtype})

        # Create relationship
        query_rel = """
        MATCH (c:Card {name: $card_name})
        MATCH (s:Subtype {name: $subtype_name})
        MERGE (c)-[:HAS_SUBTYPE]->(s)
        """

        conn.execute_query(query_rel, {
            "card_name": card_name,
            "subtype_name": subtype
        })


def batch_create_subtype_relationships(conn: Neo4jConnection, cards: list[dict]):
    """
    Create subtype relationships for all cards.

    Args:
        conn: Neo4j connection
        cards: List of card dicts with subtypes
    """
    total = len(cards)
    processed = 0

    print(f"Creating subtype relationships for {total} cards...")

    for card in cards:
        if card.get("subtypes"):  # Only process cards with subtypes
            create_subtype_relationships(conn, card)
        processed += 1

        if processed % 1000 == 0:
            print(f"  Processed {processed}/{total}...")

    print(f"✓ Created subtype relationships for {processed} cards")
