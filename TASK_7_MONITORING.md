# Task #7: Service Layer Implementation - Agent Team Monitoring Dashboard

## 📊 RED PHASE STATUS ✅ COMPLETE

All failing tests written and verified. Ready for GREEN phase implementation.

---

## Team Assignments & Progress

### 🔵 Team 1: Query Service Developer (Sonnet 4.5)

**Deliverable:** `backend/app/services/query_service.py`

**RED Phase Status:** ✅ COMPLETE

| Method | Test Written | Test Status | Priority |
|--------|--------------|------------|----------|
| find_synergistic_cards() | ✅ | SKIPPED (RED) | HIGH |
| find_known_combos() | ✅ | SKIPPED (RED) | HIGH |
| find_token_generators() | ✅ | SKIPPED (RED) | MEDIUM |
| find_cards_by_role() | ✅ | SKIPPED (RED) | HIGH |
| build_deck_shell() | ✅ | SKIPPED (RED) | HIGH |
| find_combo_packages() | ✅ | SKIPPED (RED) | MEDIUM |
| find_similar_cards() | ✅ | SKIPPED (RED) | HIGH |

**Test File:** `backend/tests/unit/test_services_query.py` (7 tests)

**Implementation Checklist (for GREEN phase):**
- [ ] Create `backend/app/services/query_service.py`
- [ ] Import DeckbuildingQueries from src
- [ ] Wrap find_synergistic_cards() with error handling
- [ ] Wrap find_known_combos()
- [ ] Wrap find_token_generators()
- [ ] Wrap find_cards_by_role()
- [ ] Wrap build_deck_shell() - must return exactly 37 cards
- [ ] Wrap find_combo_packages()
- [ ] Wrap find_similar_cards()
- [ ] Add docstrings to all methods
- [ ] Run tests: `pytest backend/tests/unit/test_services_query.py -v`
- [ ] Verify 7/7 tests PASS ✅

**Expected Implementation Time:** 2-3 hours
**Test Coverage Target:** 85%+
**Code Quality:** Type hints required, docstrings required

---

### 🔵 Team 2: Synergy Service Developer (Sonnet 4.5)

**Deliverable:** `backend/app/services/synergy_service.py`

**RED Phase Status:** ✅ COMPLETE

| Method | Test Written | Test Status | Priority |
|--------|--------------|------------|----------|
| compute_synergy_score() | ✅ | SKIPPED (RED) | CRITICAL |
| compute_synergy_dimensions_breakdown() | ✅ | SKIPPED (RED) | CRITICAL |
| find_mechanic_synergies() | ✅ | SKIPPED (RED) | HIGH |
| calculate_role_compatibility() | ✅ | SKIPPED (RED) | HIGH |

**Test File:** `backend/tests/unit/test_services_synergy.py` (4 tests)

**Implementation Checklist (for GREEN phase):**
- [ ] Create `backend/app/services/synergy_service.py`
- [ ] Import CardSynergyEngine from src
- [ ] Wrap compute_synergy_score() - returns (float, dict)
- [ ] Validate 7-dimensional breakdown in response
- [ ] Wrap find_mechanic_synergies()
- [ ] Wrap calculate_role_compatibility()
- [ ] Add error handling for missing fields
- [ ] Implement dimension weights correctly
- [ ] Add docstrings to all methods
- [ ] Run tests: `pytest backend/tests/unit/test_services_synergy.py -v`
- [ ] Verify 4/4 tests PASS ✅

**Expected Implementation Time:** 2-3 hours
**Test Coverage Target:** 85%+
**Code Quality:** Type hints required, docstrings required

**Critical Notes:**
- Must validate all 7 dimensions present: mechanic_overlap, role_compatibility, theme_alignment, zone_chain, phase_alignment, color_compatibility, type_synergy
- Weights: 0.20, 0.25, 0.20, 0.15, 0.10, 0.05, 0.05 respectively
- Synergy score must be 0-1 range

---

### 🔵 Team 3: Recommendation Service Developer (Sonnet 4.5)

**Deliverable:** `backend/app/services/recommendation_service.py`

**RED Phase Status:** ✅ COMPLETE

| Method | Test Written | Test Status | Priority |
|--------|--------------|------------|----------|
| get_embedding_recommendations() | ✅ | SKIPPED (RED) | HIGH |
| get_similarity_recommendations() | ✅ | SKIPPED (RED) | HIGH |
| ensemble_recommendations() | ✅ | SKIPPED (RED) | CRITICAL |
| get_role_based_recommendations() | ✅ | SKIPPED (RED) | HIGH |

**Test File:** `backend/tests/unit/test_services_recommendations.py` (4 tests)

**Implementation Checklist (for GREEN phase):**
- [ ] Create `backend/app/services/recommendation_service.py`
- [ ] Import recommendation functions from src
- [ ] Implement get_embedding_recommendations()
- [ ] Implement get_similarity_recommendations()
- [ ] Implement ensemble_recommendations() with weight combination
- [ ] Ensure results sorted by synergy_score descending
- [ ] Return RecommendationResponse objects
- [ ] Validate score range 0-1
- [ ] Add category field (mechanic_based, embedding_similarity, etc.)
- [ ] Add docstrings to all methods
- [ ] Run tests: `pytest backend/tests/unit/test_services_recommendations.py -v`
- [ ] Verify 4/4 tests PASS ✅

**Expected Implementation Time:** 2-3 hours
**Test Coverage Target:** 85%+
**Code Quality:** Type hints required, docstrings required

**Critical Notes:**
- Ensemble weights must be configurable: mechanic_based, embedding_similarity, role_based, community_boost
- Results must be sorted descending by synergy_score
- All scores must be normalized 0-1

---

### 🔍 QA Lead (Opus 4.6) - Monitoring All Teams

**Monitoring Checklist:**

- [ ] Day 1: Review test specs
  - Validate test quality matches TDD standards
  - Check for edge cases coverage
  - Verify test names are descriptive

- [ ] Day 2-3: Monitor GREEN phase implementation
  - Track % of tests passing per team
  - Monitor code quality (type hints, docstrings)
  - Watch for over-engineering

- [ ] Day 4: Final validation before merge
  - Run coverage report: `pytest backend/tests/unit/test_services_*.py --cov=app/services --cov-report=html`
  - Verify coverage >= 85%
  - Check for error handling in all services
  - Validate type hints on all methods

**Coverage Targets:**
```
Query Service:          Target 85%+ coverage
Synergy Service:        Target 85%+ coverage
Recommendation Service: Target 85%+ coverage
Total Service Layer:    Target 85%+ coverage
```

---

## 📋 Test Summary

### Total Service Layer Tests: 15

```
✅ Query Service:        7 tests written (SKIPPED - RED phase)
✅ Synergy Service:      4 tests written (SKIPPED - RED phase)
✅ Recommendation Svc:   4 tests written (SKIPPED - RED phase)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ TOTAL:              15 tests written (SKIPPED - RED phase)
```

### Current Status:
- **15/15 tests written** ✅
- **0/15 tests passing** (expected - RED phase)
- **Services not yet implemented** (GREEN phase next)

---

## 🚀 GREEN Phase Workflow

### For Each Team (Sequential):

**Phase 1: Implementation (Day 1-2)**
1. Create service file (query_service.py, synergy_service.py, or recommendation_service.py)
2. Import existing functions from src/
3. Create wrapper methods matching test signatures
4. Add type hints to all parameters and returns
5. Run tests: `pytest backend/tests/unit/test_services_<name>.py -v`

**Phase 2: Validation (Day 2-3)**
6. Ensure all N tests PASS ✅
7. Run coverage: `pytest backend/tests/unit/test_services_<name>.py --cov=app/services.<name> --cov-report=term`
8. Fix any coverage gaps
9. Verify no type errors: `python -m mypy backend/app/services/<name>.py` (optional)

**Phase 3: Integration (Day 3)**
10. Run ALL service tests together: `pytest backend/tests/unit/test_services_*.py -v`
11. Verify no conflicts between teams
12. Check total coverage >= 85%

---

## 📊 Daily Standup Template

Use this for daily check-ins:

```
🔵 Query Service Team:
- Status: [Not Started | In Progress | Testing | Complete]
- Tests Passing: X/7
- Blockers: [None | list any]
- Next: [what's next]

🔵 Synergy Service Team:
- Status: [Not Started | In Progress | Testing | Complete]
- Tests Passing: X/4
- Blockers: [None | list any]
- Next: [what's next]

🔵 Recommendation Service Team:
- Status: [Not Started | In Progress | Testing | Complete]
- Tests Passing: X/4
- Blockers: [None | list any]
- Next: [what's next]

🔍 QA Lead:
- Test Quality: [Approved | Review Needed]
- Coverage: X%
- Concerns: [None | list any]

Tech Lead Summary:
- Overall Progress: X%
- Risk Level: [Low | Medium | High]
- Escalations: [if any]
```

---

## 🔗 Integration Points

### Cross-Team Coordination:

**QueryService → Recommendation Service:**
- QueryService provides card data
- RecommendationService uses card data for scoring

**SynergyService → RecommendationService:**
- SynergyService computes synergy scores
- RecommendationService uses scores for ensemble

**All Services → API Routers (Task #8):**
- Routers will call services
- Routers will use services in integration tests

---

## 📈 Success Criteria for Task #7

```
✅ RED Phase Complete:
   - 15 tests written
   - All tests skipped (services not implemented)
   - Test signatures documented

✅ GREEN Phase Success:
   - 15/15 tests PASS
   - 85%+ coverage achieved
   - Type hints on all methods
   - Docstrings on all methods
   - No over-engineering
   - Minimal code (only what passes tests)

✅ Quality Gates:
   - No import errors
   - No type errors
   - No undocumented methods
   - All tests reproducible
```

---

## Commands for Each Team

### Query Service Team:

```bash
# Watch your tests
pytest backend/tests/unit/test_services_query.py -v --tb=short

# Check coverage
pytest backend/tests/unit/test_services_query.py --cov=app/services.query_service --cov-report=term

# Run with live output
pytest backend/tests/unit/test_services_query.py -v -s
```

### Synergy Service Team:

```bash
# Watch your tests
pytest backend/tests/unit/test_services_synergy.py -v --tb=short

# Check coverage
pytest backend/tests/unit/test_services_synergy.py --cov=app/services.synergy_service --cov-report=term
```

### Recommendation Service Team:

```bash
# Watch your tests
pytest backend/tests/unit/test_services_recommendations.py -v --tb=short

# Check coverage
pytest backend/tests/unit/test_services_recommendations.py --cov=app/services.recommendation_service --cov-report=term
```

### All Teams Together:

```bash
# Run all service tests
pytest backend/tests/unit/test_services_*.py -v

# Check total coverage
pytest backend/tests/unit/test_services_*.py --cov=app/services --cov-report=html

# Run with verbose output
pytest backend/tests/unit/test_services_*.py -v -s
```

---

## 📝 Notes for GREEN Phase

1. **Don't look at existing code** while writing services
   - Use the code-explorer analysis document
   - Wrap existing functions, don't rewrite them

2. **Minimal implementation**
   - Only code needed to pass tests
   - No extra configuration or options
   - No pre-optimization

3. **Type safety**
   - All parameters must have type hints
   - All returns must have type hints
   - Use Pydantic models where possible

4. **Error handling**
   - Tests will verify error cases
   - Don't add try/except unless test requires it
   - Let exceptions bubble up (TDD principle)

5. **Testing strategy**
   - Run tests frequently (after each method)
   - Stop and fix failures immediately
   - Don't move to next method until current passes

---

**Dashboard Version:** 1.0
**Last Updated:** Task #7 RED phase complete
**Ready for:** GREEN phase implementation
