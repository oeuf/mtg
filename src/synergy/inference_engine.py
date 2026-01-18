"""Infer synergies between commanders and mechanics."""

from src.graph.connection import Neo4jConnection


class SynergyInferenceEngine:
    """Infer synergies between commanders and mechanics."""

    @staticmethod
    def analyze_commander(conn: Neo4jConnection, commander_name: str):
        """Analyze commander oracle text to determine synergies."""

        # Get commander data
        query = """
        MATCH (c:Commander {name: $name})
        RETURN c.oracle_text AS oracle_text,
               c.keywords AS keywords,
               c.mechanics AS mechanics
        """
        result = conn.execute_query(query, {"name": commander_name})

        if not result:
            print(f"⚠ Commander '{commander_name}' not found")
            return

        oracle_text = result[0]["oracle_text"].lower()
        keywords = result[0].get("keywords", [])
        existing_mechanics = result[0].get("mechanics", [])

        synergies = []

        # ETB synergy
        if "enters the battlefield" in oracle_text or "etb_trigger" in existing_mechanics:
            synergies.append({
                "mechanic": "etb_trigger",
                "synergy_type": "triggers_on",
                "strength": 0.9,
                "reason": "Commander triggers or benefits from ETBs"
            })

        # Dies/sacrifice synergy
        if any(word in oracle_text for word in ["dies", "sacrific", "death trigger"]):
            synergies.append({
                "mechanic": "dies_trigger",
                "synergy_type": "triggers_on",
                "strength": 0.9,
                "reason": "Commander triggers on deaths"
            })
            synergies.append({
                "mechanic": "sacrifice_outlet",
                "synergy_type": "benefits_from",
                "strength": 0.8,
                "reason": "Synergizes with sacrifice outlets"
            })

        # Cast trigger synergy
        if "whenever you cast" in oracle_text or "cast_trigger" in existing_mechanics:
            synergies.append({
                "mechanic": "cast_trigger",
                "synergy_type": "triggers_on",
                "strength": 0.8,
                "reason": "Commander triggers on spell casts"
            })

        # Graveyard synergy
        if "from your graveyard" in oracle_text or "graveyard" in oracle_text:
            synergies.append({
                "mechanic": "recursion",
                "synergy_type": "enables",
                "strength": 0.9,
                "reason": "Commander enables graveyard strategies"
            })

        # Token synergy
        if "token" in oracle_text:
            synergies.append({
                "mechanic": "token_generation",
                "synergy_type": "benefits_from",
                "strength": 0.8,
                "reason": "Commander synergizes with tokens"
            })

        # Cost reduction synergy
        if "cost" in oracle_text and "less" in oracle_text:
            synergies.append({
                "mechanic": "cost_reduction",
                "synergy_type": "provides",
                "strength": 0.7,
                "reason": "Commander reduces costs"
            })

        # Card draw synergy
        if "draw" in oracle_text:
            synergies.append({
                "mechanic": "card_draw",
                "synergy_type": "provides",
                "strength": 0.7,
                "reason": "Commander provides card draw"
            })

        # Create relationships
        for synergy in synergies:
            query_synergy = """
            MATCH (c:Commander {name: $commander_name})
            MERGE (m:Mechanic {name: $mechanic_name})
            MERGE (c)-[:SYNERGIZES_WITH_MECHANIC {
                synergy_type: $synergy_type,
                strength: $strength,
                reason: $reason
            }]->(m)
            """

            conn.execute_query(query_synergy, {
                "commander_name": commander_name,
                "mechanic_name": synergy["mechanic"],
                "synergy_type": synergy["synergy_type"],
                "strength": synergy["strength"],
                "reason": synergy["reason"]
            })

        print(f"✓ Analyzed '{commander_name}': found {len(synergies)} synergies")
        return synergies
