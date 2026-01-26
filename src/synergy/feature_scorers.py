"""Modular scoring functions for different card property dimensions."""

from typing import List, Dict, Tuple
import math


class FeatureScorers:
    """Collection of scoring functions for card property dimensions."""

    # Weight configuration for ensemble scoring
    DIMENSION_WEIGHTS = {
        "mechanic_overlap": 0.20,
        "role_compatibility": 0.25,
        "theme_alignment": 0.20,
        "zone_chain": 0.15,
        "phase_alignment": 0.10,
        "color_compatibility": 0.05,
        "type_synergy": 0.05
    }

    # Role complementarity matrix (from existing ROLE_SYNERGIES)
    ROLE_COMPATIBILITY = {
        ("etb_trigger", "sacrifice_outlet"): 0.9,
        ("etb_trigger", "recursion"): 0.85,
        ("dies_trigger", "sacrifice_outlet"): 0.95,
        ("recursion", "self_mill"): 0.8,
        ("token_generation", "sacrifice_outlet"): 0.85,
        ("ramp", "card_draw"): 0.6,
        ("removal", "protection"): 0.5,
    }

    # Theme compatibility matrix (strategic alignment)
    THEME_COMPATIBILITY = {
        ("reanimation", "graveyard_value"): 0.95,
        ("reanimation", "self_mill"): 0.90,
        ("aristocrats", "tokens"): 0.85,
        ("aristocrats", "dies_trigger"): 0.90,
        ("tokens", "anthem"): 0.85,
        ("spellslinger", "draw_engines"): 0.80,
        ("blink", "etb_trigger"): 0.95,
        ("counters", "proliferate"): 0.90,
        # Add more as discovered
    }

    @staticmethod
    def score_mechanic_overlap(mechanics1: List[str], mechanics2: List[str]) -> Tuple[float, Dict]:
        """Score based on shared mechanics (existing logic enhanced)."""
        if not mechanics1 or not mechanics2:
            return 0.0, {"shared": []}

        shared = set(mechanics1) & set(mechanics2)

        if not shared:
            return 0.0, {"shared": []}

        # Enhanced scoring:
        # - Jaccard similarity (set overlap)
        # - Bonus for high overlap (diminishing returns after 3)
        union = set(mechanics1) | set(mechanics2)
        jaccard = len(shared) / len(union)

        # Bonus for absolute count (capped at 5)
        count_bonus = min(len(shared), 5) / 5.0

        score = (jaccard * 0.6) + (count_bonus * 0.4)

        return score, {
            "shared": list(shared),
            "count": len(shared),
            "jaccard": jaccard
        }

    @staticmethod
    def score_role_compatibility(roles1: List[str], roles2: List[str]) -> Tuple[float, Dict]:
        """Score based on role complementarity (enabler + payoff)."""
        if not roles1 or not roles2:
            return 0.0, {"matches": []}

        max_score = 0.0
        best_pair = None
        all_matches = []

        for r1 in roles1:
            for r2 in roles2:
                # Check both directions
                score = max(
                    FeatureScorers.ROLE_COMPATIBILITY.get((r1, r2), 0.0),
                    FeatureScorers.ROLE_COMPATIBILITY.get((r2, r1), 0.0)
                )
                if score > 0:
                    all_matches.append({
                        "pair": (r1, r2),
                        "score": score
                    })
                    if score > max_score:
                        max_score = score
                        best_pair = (r1, r2)

        # Penalty if roles are identical (redundancy)
        if set(roles1) & set(roles2):
            max_score *= 0.3

        return max_score, {
            "best_pair": best_pair,
            "matches": all_matches
        }

    @staticmethod
    def score_theme_alignment(themes1: List[str], themes2: List[str]) -> Tuple[float, Dict]:
        """Score based on thematic alignment (strategy compatibility)."""
        if not themes1 or not themes2:
            return 0.0, {"shared": [], "complementary": []}

        shared = set(themes1) & set(themes2)

        # Shared themes = strong alignment
        if shared:
            shared_score = len(shared) / max(len(themes1), len(themes2))
        else:
            shared_score = 0.0

        # Complementary themes (different but synergistic)
        comp_score = 0.0
        comp_pairs = []
        for t1 in themes1:
            for t2 in themes2:
                if t1 != t2:
                    score = max(
                        FeatureScorers.THEME_COMPATIBILITY.get((t1, t2), 0.0),
                        FeatureScorers.THEME_COMPATIBILITY.get((t2, t1), 0.0)
                    )
                    if score > comp_score:
                        comp_score = score
                        comp_pairs.append((t1, t2, score))

        # Weighted combination
        final_score = (shared_score * 0.7) + (comp_score * 0.3)

        return final_score, {
            "shared": list(shared),
            "complementary": comp_pairs
        }

    @staticmethod
    def score_zone_chain(zones1: List[Dict], zones2: List[Dict]) -> Tuple[float, Dict]:
        """Score based on zone interaction chains (enabler -> payoff)."""
        if not zones1 or not zones2:
            return 0.0, {"chains": []}

        chains = []

        # Look for write -> read chains
        for z1 in zones1:
            for z2 in zones2:
                if z1["zone"] == z2["zone"]:
                    # Same zone interaction
                    if z1["interaction_type"] == "writes" and z2["interaction_type"] == "reads":
                        chains.append({
                            "zone": z1["zone"],
                            "type": "write_read",
                            "score": 0.8
                        })
                    elif z1["interaction_type"] == "reads" and z2["interaction_type"] == "writes":
                        chains.append({
                            "zone": z1["zone"],
                            "type": "read_write",
                            "score": 0.6
                        })
                    elif z1["interaction_type"] == z2["interaction_type"]:
                        chains.append({
                            "zone": z1["zone"],
                            "type": "same_interaction",
                            "score": 0.4
                        })

        if not chains:
            return 0.0, {"chains": []}

        # Take max score from all chains
        max_score = max(c["score"] for c in chains)

        return max_score, {"chains": chains}

    @staticmethod
    def score_phase_alignment(phases1: List[Dict], phases2: List[Dict]) -> Tuple[float, Dict]:
        """Score based on phase trigger alignment."""
        if not phases1 or not phases2:
            return 0.0, {"shared_phases": []}

        phases1_set = {p["phase"] for p in phases1}
        phases2_set = {p["phase"] for p in phases2}

        shared = phases1_set & phases2_set

        if not shared:
            return 0.0, {"shared_phases": []}

        # Jaccard similarity
        union = phases1_set | phases2_set
        score = len(shared) / len(union)

        return score, {
            "shared_phases": list(shared),
            "count": len(shared)
        }

    @staticmethod
    def score_color_compatibility(colors1: List[str], colors2: List[str]) -> Tuple[float, Dict]:
        """Score based on color identity overlap (castability in same deck)."""
        if not colors1 or not colors2:
            # Colorless compatibility
            if not colors1 and not colors2:
                return 1.0, {"type": "both_colorless"}
            elif not colors1 or not colors2:
                return 0.9, {"type": "one_colorless"}

        colors1_set = set(colors1)
        colors2_set = set(colors2)

        # Exact match = perfect
        if colors1_set == colors2_set:
            return 1.0, {"type": "exact_match"}

        # Subset = very good (one card is easier to cast)
        if colors1_set.issubset(colors2_set) or colors2_set.issubset(colors1_set):
            return 0.95, {"type": "subset"}

        # Overlapping colors = good
        overlap = colors1_set & colors2_set
        if overlap:
            # Penalty for additional colors needed
            extra_colors = len((colors1_set | colors2_set) - overlap)
            score = 0.8 - (extra_colors * 0.1)
            return max(score, 0.3), {"type": "overlap", "shared": list(overlap)}

        # Completely different colors = still possible but harder
        return 0.3, {"type": "disjoint"}

    @staticmethod
    def score_type_synergy(subtypes1: List[str], subtypes2: List[str],
                          type_line1: str, type_line2: str) -> Tuple[float, Dict]:
        """Score based on shared types/subtypes (tribal, artifact/enchantment matters)."""
        score = 0.0
        details = {}

        # Shared creature types (tribal synergy)
        if subtypes1 and subtypes2:
            shared_subtypes = set(subtypes1) & set(subtypes2)
            if shared_subtypes:
                score += 0.7
                details["shared_subtypes"] = list(shared_subtypes)

        # Shared card types (Artifact, Enchantment, etc.)
        types1 = set(type_line1.split("—")[0].strip().split())
        types2 = set(type_line2.split("—")[0].strip().split())
        shared_types = types1 & types2

        if shared_types:
            score += 0.3
            details["shared_types"] = list(shared_types)

        return min(score, 1.0), details

    @classmethod
    def calculate_ensemble_score(cls, dimension_scores: Dict[str, Tuple[float, Dict]]) -> Tuple[float, Dict]:
        """Combine all dimension scores into final synergy score."""
        weighted_sum = 0.0
        details = {}

        for dimension, (score, info) in dimension_scores.items():
            weight = cls.DIMENSION_WEIGHTS.get(dimension, 0.0)
            weighted_sum += score * weight
            details[dimension] = {
                "score": score,
                "weight": weight,
                "weighted_score": score * weight,
                "info": info
            }

        details["final_score"] = weighted_sum

        return weighted_sum, details
