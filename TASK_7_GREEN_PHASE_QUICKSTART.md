# Task #7 GREEN Phase - Quick Start Guide

**Status:** Ready to begin ⏳
**Timeline:** 2-3 days for all 3 teams
**Oversight:** Tech Lead (Sonnet 4.5) + QA Lead (Opus 4.6)

---

## For Each Backend Developer

### Pre-Implementation Checklist

Before you start, verify:

```bash
# 1. Activate venv
source backend_venv/bin/activate

# 2. Run tests to verify RED phase
pytest backend/tests/unit/test_services_*.py -v --tb=no

# Expected output:
# ✅ 15 tests SKIPPED (correct - services don't exist yet)
# ✅ 0 tests FAILED (correct - no imports failing yet)

# 3. Verify existing code exists
python -c "from src.synergy.queries import DeckbuildingQueries; print('✅ DeckbuildingQueries available')"
python -c "from src.synergy.card_synergies import CardSynergyEngine; print('✅ CardSynergyEngine available')"

# 4. Create __init__.py in services if not present
touch backend/app/services/__init__.py
```

---

## 🔵 Team 1: QueryService Implementation

**Test File:** `backend/tests/unit/test_services_query.py` (7 tests)
**Deliverable:** `backend/app/services/query_service.py`

### Step 1: Create Service File

```bash
touch backend/app/services/query_service.py
```

### Step 2: Implement Methods (One at a Time)

**Follow this order - run tests after each method:**

```python
# File: backend/app/services/query_service.py

from typing import List, Dict, Any, Optional
from neo4j import Session

class QueryService:
    """Wraps DeckbuildingQueries for API layer."""

    def __init__(self, session: Session):
        self.session = session
        # Import at runtime to avoid circular imports
        from src.synergy.queries import DeckbuildingQueries
        self.queries = DeckbuildingQueries(session)

    # Method 1: find_synergistic_cards
    def find_synergistic_cards(
        self,
        commander_name: str,
        max_cmc: int = 4,
        min_strength: float = 0.7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Find cards that synergize with commander."""
        # Wrap self.queries.find_synergistic_cards()
        pass

    # Method 2: find_known_combos
    def find_known_combos(self, card_names: List[str]) -> List[Dict[str, Any]]:
        """Find known combos for given cards."""
        # Wrap self.queries.find_known_combos()
        pass

    # Method 3: find_token_generators
    def find_token_generators(
        self,
        commander_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find cards that generate tokens."""
        # Wrap self.queries.find_token_generators()
        pass

    # Method 4: find_cards_by_role
    def find_cards_by_role(
        self,
        role: str,
        color_identity: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Find cards with specific functional role."""
        # Wrap self.queries.find_cards_by_role()
        pass

    # Method 5: build_deck_shell (CRITICAL: must return exactly 37 cards)
    def build_deck_shell(self, commander_name: str) -> List[Dict[str, Any]]:
        """Build deck shell (37 cards) for commander."""
        # Wrap self.queries.build_deck_shell()
        # CRITICAL: Result must have exactly 37 cards
        pass

    # Method 6: find_combo_packages
    def find_combo_packages(
        self,
        commander_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Find combo packages that work with commander."""
        # Wrap self.queries.find_combo_packages()
        pass

    # Method 7: find_similar_cards
    def find_similar_cards(
        self,
        card_name: str,
        limit: int = 20,
        method: str = "embedding"
    ) -> List[Dict[str, Any]]:
        """Find cards similar to given card."""
        # Wrap self.queries.find_similar_cards()
        pass
```

### Step 3: Run Tests After Each Method

```bash
# After implementing each method, run:
pytest backend/tests/unit/test_services_query.py::TestQueryService::<method_name> -v

# Example:
pytest backend/tests/unit/test_services_query.py::TestQueryService::test_find_synergistic_cards_returns_list -v

# Stop and fix any failures immediately. Don't move to next method until current passes.
```

### Step 4: Verify All Tests Pass & Coverage

```bash
# Run all 7 tests
pytest backend/tests/unit/test_services_query.py -v

# Check coverage
pytest backend/tests/unit/test_services_query.py --cov=app.services.query_service --cov-report=term

# Should see: ✅ 7 passed + Coverage >= 85%
```

---

## 🔵 Team 2: SynergyService Implementation

**Test File:** `backend/tests/unit/test_services_synergy.py` (4 tests)
**Deliverable:** `backend/app/services/synergy_service.py`

### Step 1: Create Service File

```bash
touch backend/app/services/synergy_service.py
```

### Step 2: Implement Methods (One at a Time)

**Critical:** All 7 dimensions must be present in responses

```python
# File: backend/app/services/synergy_service.py

from typing import Dict, List, Tuple, Any, Optional
from neo4j import Session
from app.models.synergy import SynergyDimensions, SynergyResponse

class SynergyService:
    """Wraps CardSynergyEngine for synergy scoring."""

    def __init__(self, session: Session):
        self.session = session
        from src.synergy.card_synergies import CardSynergyEngine
        self.engine = CardSynergyEngine(session)

    # Method 1: compute_synergy_score
    def compute_synergy_score(
        self,
        card1_name: str,
        card2_name: str
    ) -> Tuple[float, Dict[str, Any]]:
        """Compute synergy score between two cards.

        Returns:
            (score, dimensions_dict) where dimensions_dict includes all 7 dimensions
        """
        # Wrap self.engine.compute_synergy_score()
        # Returns: (score: float 0-1, details: dict with all 7 dimension breakdowns)
        pass

    # Method 2: compute_synergy_dimensions_breakdown
    def compute_synergy_dimensions_breakdown(
        self,
        card1_name: str,
        card2_name: str
    ) -> SynergyDimensions:
        """Get detailed 7-dimensional synergy breakdown.

        CRITICAL: Must validate all 7 dimensions present:
        - mechanic_overlap (20%)
        - role_compatibility (25%)
        - theme_alignment (20%)
        - zone_chain (15%)
        - phase_alignment (10%)
        - color_compatibility (5%)
        - type_synergy (5%)
        """
        # Wrap self.engine methods to return all 7 dimensions
        # Validate none are missing
        pass

    # Method 3: find_mechanic_synergies
    def find_mechanic_synergies(
        self,
        card_name: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Find cards with mechanic synergies."""
        # Wrap self.engine.find_mechanic_synergies()
        pass

    # Method 4: calculate_role_compatibility
    def calculate_role_compatibility(
        self,
        card1_name: str,
        card2_name: str
    ) -> float:
        """Calculate role compatibility score (0-1)."""
        # Wrap self.engine.calculate_role_compatibility()
        pass
```

### Step 3: Verify 7-Dimension Validation

**Critical test to verify locally:**

```python
# In test or interactively:
service = SynergyService(session)
score, dims = service.compute_synergy_score("Eternal Witness", "Muldrotha, the Gravetide")

# Must have these exact 7 keys:
required_dims = {
    'mechanic_overlap', 'role_compatibility', 'theme_alignment',
    'zone_chain', 'phase_alignment', 'color_compatibility', 'type_synergy'
}

assert set(dims.keys()) >= required_dims, f"Missing dimensions: {required_dims - set(dims.keys())}"
assert all(isinstance(v, (int, float)) for v in dims.values()), "All dimensions must be numbers"
assert 0 <= score <= 1, f"Score must be 0-1, got {score}"
```

### Step 4: Run Tests

```bash
# Run all 4 tests
pytest backend/tests/unit/test_services_synergy.py -v

# Check coverage
pytest backend/tests/unit/test_services_synergy.py --cov=app.services.synergy_service --cov-report=term

# Should see: ✅ 4 passed + Coverage >= 85%
```

---

## 🔵 Team 3: RecommendationService Implementation

**Test File:** `backend/tests/unit/test_services_recommendations.py` (4 tests)
**Deliverable:** `backend/app/services/recommendation_service.py`

### Step 1: Create Service File

```bash
touch backend/app/services/recommendation_service.py
```

### Step 2: Implement Methods (One at a Time)

**Critical:** Results must be sorted descending by synergy_score

```python
# File: backend/app/services/recommendation_service.py

from typing import List, Dict, Optional, Any
from neo4j import Session
from app.models.synergy import RecommendationResponse

class RecommendationService:
    """Ensemble recommendation engine."""

    def __init__(self, session: Session):
        self.session = session
        # Import supporting services
        from app.services.query_service import QueryService
        from app.services.synergy_service import SynergyService
        self.query_service = QueryService(session)
        self.synergy_service = SynergyService(session)

    # Method 1: get_embedding_recommendations
    def get_embedding_recommendations(
        self,
        commander_name: str,
        top_k: int = 20
    ) -> List[RecommendationResponse]:
        """Get recommendations based on FastRP embedding similarity.

        Returns:
            List sorted by synergy_score descending, all scores 0-1,
            category='embedding_similarity'
        """
        # Query Neo4j for EMBEDDING_SIMILAR relationships
        # Return as RecommendationResponse with category='embedding_similarity'
        pass

    # Method 2: get_similarity_recommendations
    def get_similarity_recommendations(
        self,
        commander_name: str,
        top_k: int = 20
    ) -> List[RecommendationResponse]:
        """Get recommendations based on kNN similarity.

        Returns:
            List sorted by synergy_score descending, all scores 0-1,
            category='similarity_based'
        """
        # Use existing similarity relationships
        # Return as RecommendationResponse with category='similarity_based'
        pass

    # Method 3: ensemble_recommendations (CRITICAL: combines all approaches)
    def ensemble_recommendations(
        self,
        commander_name: str,
        top_k: int = 30,
        weights: Optional[Dict[str, float]] = None
    ) -> List[RecommendationResponse]:
        """Combine all recommendation sources with configurable weights.

        Default weights:
        {
            'mechanic_based': 0.3,
            'embedding_similarity': 0.3,
            'role_based': 0.25,
            'community_boost': 0.15
        }

        Returns:
            List sorted by synergy_score descending (highest first),
            all scores normalized 0-1
        """
        # Get recommendations from all sources
        # Combine with weights
        # Sort by score descending (CRITICAL)
        # Normalize scores to 0-1
        pass

    # Method 4: get_role_based_recommendations
    def get_role_based_recommendations(
        self,
        commander_name: str,
        top_k: int = 20
    ) -> List[RecommendationResponse]:
        """Get recommendations based on functional roles.

        Returns:
            List sorted by synergy_score descending, all scores 0-1,
            category='role_based'
        """
        # Use role compatibility from SynergyService
        # Return as RecommendationResponse with category='role_based'
        pass
```

### Step 3: Verify Ensemble Sorting (Critical!)

**Test locally:**

```python
# Verify results are sorted descending
service = RecommendationService(session)
result = service.ensemble_recommendations("Muldrotha, the Gravetide", top_k=30)

scores = [r.synergy_score for r in result]
assert scores == sorted(scores, reverse=True), "Results must be sorted by score descending"
assert all(0 <= s <= 1 for s in scores), "All scores must be 0-1"
```

### Step 4: Run Tests

```bash
# Run all 4 tests
pytest backend/tests/unit/test_services_recommendations.py -v

# Check coverage
pytest backend/tests/unit/test_services_recommendations.py --cov=app.services.recommendation_service --cov-report=term

# Should see: ✅ 4 passed + Coverage >= 85%
```

---

## After Implementation: Verification

### Step 1: All Teams - Run Combined Tests

```bash
# Run all 15 service tests together
pytest backend/tests/unit/test_services_*.py -v

# Expected: ✅ 15 passed
```

### Step 2: All Teams - Check Total Coverage

```bash
pytest backend/tests/unit/test_services_*.py --cov=app.services --cov-report=html

# Open report: open htmlcov/index.html
# Should see: >= 85% coverage
```

### Step 3: Tech Lead - Approve All Services

```bash
# Tech Lead runs final validation:
pytest backend/tests/unit/test_services_*.py -v --tb=short
pytest backend/tests/unit/ -v --cov=app --cov-report=term

# Verifies:
# ✅ All 15 tests PASS
# ✅ Coverage >= 85%
# ✅ No import errors
# ✅ Type hints visible
```

### Step 4: QA Lead - Code Review

Run with agents:
- `pr-review-toolkit:code-reviewer` - Check quality standards
- `pr-review-toolkit:code-simplifier` - Simplify complex logic
- `pr-review-toolkit:silent-failure-hunter` - Verify error handling
- `pr-review-toolkit:comment-analyzer` - Verify docstrings

---

## Troubleshooting

### Issue: Neo4j Connection Failed
```bash
# Verify Neo4j is running
docker ps | grep mtg-neo4j

# If not running:
docker-compose up -d neo4j
sleep 10

# Test connection
python -c "from src.graph.connection import Neo4jDriver; driver = Neo4jDriver('bolt://localhost:7687', 'neo4j', 'password'); print('✅ Connected')"
```

### Issue: Import Errors (existing code not found)
```bash
# Verify PYTHONPATH includes src/
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Test import:
python -c "from src.synergy.queries import DeckbuildingQueries; print('✅ OK')"
```

### Issue: Tests Still Skipped (not running)
```bash
# Check test file - remove pytest.skip() at top of each test
# Example - should NOT have this:
# pytest.skip("Service not yet implemented - RED phase")

# Remove that line and tests should run
```

### Issue: Coverage Not 85%
```bash
# Check which lines aren't covered:
pytest backend/tests/unit/test_services_query.py --cov=app.services.query_service --cov-report=term-missing

# Add missing tests or improve implementation coverage
```

---

## Success Criteria

**GREEN Phase is DONE when:**

- ✅ All 15 tests PASS (7 + 4 + 4)
- ✅ 85%+ code coverage
- ✅ Type hints on all methods
- ✅ Docstrings on all methods
- ✅ Zero over-engineering (minimal code)
- ✅ No import or type errors
- ✅ Code passed through code-simplifier
- ✅ Code passed through code-reviewer
- ✅ Tech Lead approved
- ✅ Lead Architect approved

**Then → Task #8 (API Routers) begins**

---

## Communication

**Daily Standup (to Tech Lead):**
```
Team [#]: QueryService | SynergyService | RecommendationService
- Tests Passing: X/Y
- Coverage: Z%
- Blockers: [none or description]
- Next: [next method or deadline]
```

**Escalations:**
If you're stuck for > 30 min, contact Tech Lead immediately.
Tech Lead will escalate to Lead Architect if needed.

---

**Good luck! Follow TDD discipline: Run tests frequently, fix failures immediately, no over-engineering.** ✅
