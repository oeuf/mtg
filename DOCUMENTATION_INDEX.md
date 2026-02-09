# MTG Commander Web Application - Documentation Index

**Last Updated:** February 8, 2026 - Agent Teams + TDD Integration Complete
**Project Status:** Milestone 1 - 73% Complete (Ready for Task #7 GREEN Phase)

---

## Quick Navigation

### 🎯 I Need To...

**Start Task #7 GREEN Phase (Service Implementation)**
→ Read: `TASK_7_GREEN_PHASE_QUICKSTART.md`

**Understand Current Team Assignments**
→ Read: `AGENT_TEAM_PROGRESS.md` (comprehensive tracking)
→ Or: `~/.claude/plans/immutable-hopping-wall.md` (full plan)

**Monitor Daily Progress**
→ Use: `TASK_7_MONITORING.md` (dashboard template)
→ Report: Use standup template

**Understand Overall Project**
→ Read: `PROJECT_STATUS_REPORT.md` (health & progress)

**Get Detailed Roadmap**
→ Read: `IMPLEMENTATION_PLAN.md` (8-week breakdown)

**See What Changed Today**
→ Read: `REVISION_SUMMARY.md` (what was updated)

---

## Document Map

### Strategic Planning Documents

#### `~/.claude/plans/immutable-hopping-wall.md` (Master Plan)
- **Type:** Strategic reference document
- **Size:** ~16 KB
- **Audience:** Lead Architect, Tech Lead, Project Stakeholders
- **Contents:**
  - Agent Team Structure with full assignments
  - TDD Strategy & Workflow
  - Current Project Status (73% complete)
  - Stories.md Questions Answers
  - Immediate Next Steps for each team
  - Daily Standup Template
  - Definition of Done
  - Tech Stack & Tools
  - Success Metrics
- **When to Use:** High-level planning, decision-making, team orientation
- **Key Sections:**
  - Part 1: Agent Teams (Leadership, Backend, QA)
  - Part 2: TDD Strategy (RED/GREEN/REFACTOR)
  - Part 5: Next Steps (with commands)

---

#### `IMPLEMENTATION_PLAN.md` (Detailed Roadmap)
- **Type:** Comprehensive implementation reference
- **Size:** ~40 KB
- **Audience:** All team members, stakeholders
- **Contents:**
  - Progress Tracking with Agent Team Milestones
  - Detailed Agent Team Assignments (13 roles)
  - TDD Strategy with test organization
  - Plugin & Skills Integration Points
  - 7 Milestones over 8 weeks
  - Verification Strategy
  - Success Metrics
- **When to Use:** Understanding full scope, architecture decisions, long-term planning
- **Key Sections:**
  - Progress Tracking (shows completed vs. pending)
  - Agent Teams Part 1 (detailed roles)
  - TDD Workflow details
  - Milestone breakdown (Weeks 1-8)

---

### Current Project Status Documents

#### `AGENT_TEAM_PROGRESS.md` (Team Tracking)
- **Type:** Current state + team assignments
- **Size:** ~17 KB
- **Audience:** Team Leads, Developers, QA
- **Contents:**
  - Team Assignments & Status (tabular)
  - Detailed Status by Role (Leadership, Backend, QA)
  - Methods to implement (with critical constraints)
  - Test Progress Tracking
  - TDD Cycle Status
  - Timeline & Milestones
  - Key Metrics & Success Criteria
  - Daily Standup Template
- **When to Use:** Daily monitoring, understanding current assignments, tracking progress
- **Key Tables:**
  - Each team member's current tasks
  - Methods to implement per team
  - Test progress (27/53 passing)
- **Update Frequency:** Daily during implementation

---

#### `PROJECT_STATUS_REPORT.md` (High-Level Health)
- **Type:** Project health snapshot
- **Size:** ~13 KB
- **Audience:** Stakeholders, Project Leads, All Teams
- **Contents:**
  - Overall Progress (73% complete)
  - Agent Team Attribution (who did what)
  - Test Summary (27 passing, 26 skipped)
  - Tasks Completed vs. Pending
  - File Structure Status
  - Deliverables by Task
  - Timeline
  - Success Metrics
- **When to Use:** Status updates, understanding progress, stakeholder reports
- **Key Metrics:**
  - Tests: 27/53 passing (51%)
  - Tasks: 6/9 complete
  - Timeline: Week 1/8

---

### Implementation Guides

#### `TASK_7_GREEN_PHASE_QUICKSTART.md` (Developer Guide)
- **Type:** Hands-on implementation guide
- **Size:** ~15 KB
- **Audience:** Backend Developers (Dev 1, 2, 3)
- **Contents:**
  - Pre-implementation Checklist
  - Step-by-step guide for each team:
    - QueryService (7 methods)
    - SynergyService (4 methods, 7 dimensions)
    - RecommendationService (4 methods, ensemble)
  - Code templates for each service
  - Test verification commands
  - Troubleshooting
  - Success Criteria Checklist
- **When to Use:** During implementation, daily reference
- **Start Command:** See "Pre-Implementation Checklist" section
- **Key Constraints Documented:**
  - build_deck_shell() must return exactly 37 cards
  - SynergyService must validate all 7 dimensions
  - RecommendationService must sort results descending

---

#### `TASK_7_MONITORING.md` (Daily Dashboard)
- **Type:** Monitoring & tracking dashboard
- **Size:** ~11 KB
- **Audience:** Tech Lead, QA Lead, Team Leads
- **Contents:**
  - Team Assignments with Checklists
  - Test Summary
  - Daily Standup Template
  - GREEN Phase Workflow
  - Commands for Each Team
  - Coverage Targets
  - Monitoring Checklist
- **When to Use:** Daily standups, progress tracking, unblocking teams
- **Key Template:** Daily Standup (copy and fill daily)

---

#### `TASK_7_RED_PHASE_SUMMARY.md` (Phase Completion Report)
- **Type:** Phase completion documentation
- **Size:** ~9 KB
- **Audience:** All teams, stakeholders
- **Contents:**
  - Achievement Summary (15 tests written)
  - TDD Cycle Progress (RED ✅, GREEN ⏳)
  - What Each Team Will Implement
  - Test Verification Output
  - GREEN Phase Handoff
  - Monitoring & Metrics
  - TDD Discipline Verified
  - Next Steps
- **When to Use:** Understanding RED phase completion, starting GREEN phase
- **Key Section:** "What Each Team Will Implement" (methods list)

---

### Summary & Updates

#### `REVISION_SUMMARY.md` (Today's Updates)
- **Type:** Change summary
- **Size:** ~8.9 KB
- **Audience:** All teams (what changed today)
- **Contents:**
  - What was updated (5 files)
  - Summary of changes to each
  - Documentation hierarchy
  - Agent teams now documented
  - Current status by document
  - Test status
  - Next steps
  - Key improvements made
  - Verification checklist
- **When to Use:** Understanding what's new, onboarding new team members
- **Key Section:** "Agent Teams Now Fully Documented"

---

#### `DOCUMENTATION_INDEX.md` (This File)
- **Type:** Navigation guide
- **Size:** This file
- **Audience:** All teams
- **Purpose:** Help find the right document for your needs

---

## By Role: Which Documents To Read

### 👨‍💼 Lead Architect (Opus 4.6)
1. **First:** `~/.claude/plans/immutable-hopping-wall.md` (full plan)
2. **Daily:** `AGENT_TEAM_PROGRESS.md` (team status)
3. **Monitor:** `TASK_7_GREEN_PHASE_QUICKSTART.md` (what devs are implementing)
4. **Approve:** Verify against `TASK_7_MONITORING.md` metrics

### 👨‍💼 Tech Lead (Sonnet 4.5)
1. **Start Here:** `AGENT_TEAM_PROGRESS.md` (full team tracking)
2. **Daily Monitor:** `TASK_7_MONITORING.md` (standup template)
3. **Reference:** `~/.claude/plans/immutable-hopping-wall.md` (decisions)
4. **Verify:** `PROJECT_STATUS_REPORT.md` (overall health)

### 👨‍💻 Backend Dev 1 (QueryService)
1. **Start:** `TASK_7_GREEN_PHASE_QUICKSTART.md` (section "Team 1")
2. **Reference:** `AGENT_TEAM_PROGRESS.md` (your methods)
3. **Daily:** Run tests listed in Quickstart
4. **Blocked?** Check `TASK_7_MONITORING.md` for escalation process

### 👨‍💻 Backend Dev 2 (SynergyService)
1. **Start:** `TASK_7_GREEN_PHASE_QUICKSTART.md` (section "Team 2")
2. **Critical:** Note 7 dimensions requirement
3. **Reference:** `AGENT_TEAM_PROGRESS.md` (your methods)
4. **Verification:** Check 7-dimension validation example

### 👨‍💻 Backend Dev 3 (RecommendationService)
1. **Start:** `TASK_7_GREEN_PHASE_QUICKSTART.md` (section "Team 3")
2. **Critical:** Note ensemble sorting requirement (descending by score)
3. **Reference:** `AGENT_TEAM_PROGRESS.md` (your methods)
4. **Verification:** Check ensemble sorting example

### 🔍 QA Lead (Opus 4.6)
1. **Daily:** `TASK_7_MONITORING.md` (coverage metrics)
2. **Status:** `AGENT_TEAM_PROGRESS.md` (tracking section)
3. **Baseline:** `TASK_7_RED_PHASE_SUMMARY.md` (test specs)
4. **Gate:** Verify against checklist in `TASK_7_MONITORING.md`

### 👨‍💻 Test Engineer (Haiku 4.5)
1. **Reference:** `TASK_7_GREEN_PHASE_QUICKSTART.md` (troubleshooting)
2. **Support:** `AGENT_TEAM_PROGRESS.md` (test progress)
3. **Debug:** Systematic-debugging skill when issues arise

---

## Document Cross-Reference

### About Agent Teams
- **Full Structure:** `IMPLEMENTATION_PLAN.md` (Part 1)
- **Current Status:** `AGENT_TEAM_PROGRESS.md` (Section 1)
- **Assignments:** `~/.claude/plans/immutable-hopping-wall.md` (Part 1)
- **Attribution:** `PROJECT_STATUS_REPORT.md` (Agent Team Attribution section)

### About TDD Cycle
- **Full Strategy:** `IMPLEMENTATION_PLAN.md` (Part 2)
- **Current Phase:** `TASK_7_RED_PHASE_SUMMARY.md` (TDD Cycle Progress)
- **Status:** `AGENT_TEAM_PROGRESS.md` (Test Progress Tracking)
- **Next Phase:** `~/.claude/plans/immutable-hopping-wall.md` (Part 2)

### About Task #7
- **RED Phase (Complete):** `TASK_7_RED_PHASE_SUMMARY.md`
- **GREEN Phase (Ready):** `TASK_7_GREEN_PHASE_QUICKSTART.md`
- **Monitoring:** `TASK_7_MONITORING.md`
- **Methods:** `AGENT_TEAM_PROGRESS.md` (Backend Team sections)

### About Progress
- **Overall:** `PROJECT_STATUS_REPORT.md` (73% complete)
- **By Team:** `AGENT_TEAM_PROGRESS.md` (status tables)
- **Tests:** `TASK_7_RED_PHASE_SUMMARY.md` (test counts)
- **Next:** `~/.claude/plans/immutable-hopping-wall.md` (Part 5)

---

## Test Status Quick Reference

```
Total Tests:    53
Passing:        27 (51%) ✅
Skipped:        26 (49%) ⏳

Breakdown:
- Models:        6 passing + 11 skipped
- API Endpoints: 21 passing (RED phase correct 404s)
- Service Layer: 0 passing + 15 skipped (GREEN phase ready)

TDD Status:
- RED Phase:  ✅ Complete (15 tests written)
- GREEN Phase: ⏳ Ready (3 teams, 2-3 days)
- REFACTOR:   ⏳ Planned (after tests pass)
```

---

## Tools & Skills Documentation

### In Active Use
- `superpowers:test-driven-development` - TDD workflow
- `pr-review-toolkit:code-reviewer` - Quality validation
- `pr-review-toolkit:code-simplifier` - Code simplification
- `pr-review-toolkit:silent-failure-hunter` - Error handling
- `feature-dev:code-explorer` - Code analysis
- `feature-dev:code-architect` - Architecture

### Documented In
- `~/.claude/plans/immutable-hopping-wall.md` (Part 8)
- `IMPLEMENTATION_PLAN.md` (Part 2 - TDD section)
- `AGENT_TEAM_PROGRESS.md` (Skills & Tools section)

---

## Quick Commands

### Before Starting Implementation
```bash
source backend_venv/bin/activate
pytest backend/tests/unit/test_services_*.py -v --tb=no
# Should see: ✅ 15 tests SKIPPED (correct - RED phase)
```

### During Implementation
```bash
# Run specific service tests
pytest backend/tests/unit/test_services_query.py -v
pytest backend/tests/unit/test_services_synergy.py -v
pytest backend/tests/unit/test_services_recommendations.py -v

# Check coverage
pytest backend/tests/unit/test_services_*.py --cov=app.services --cov-report=term
```

### After Implementation
```bash
# Run all 15 tests
pytest backend/tests/unit/test_services_*.py -v

# Generate HTML coverage report
pytest backend/tests/unit/test_services_*.py --cov=app.services --cov-report=html
open htmlcov/index.html
```

---

## File Locations

### Master Plan
- Location: `/Users/ng/.claude/plans/immutable-hopping-wall.md`
- Size: ~16 KB
- Access: User's Claude plans directory

### Project Documentation
- Location: `/Users/ng/cc-projects/mtg/`
- Files:
  - `IMPLEMENTATION_PLAN.md` (~40 KB)
  - `AGENT_TEAM_PROGRESS.md` (~17 KB)
  - `PROJECT_STATUS_REPORT.md` (~13 KB)
  - `TASK_7_GREEN_PHASE_QUICKSTART.md` (~15 KB)
  - `TASK_7_MONITORING.md` (~11 KB)
  - `TASK_7_RED_PHASE_SUMMARY.md` (~9 KB)
  - `REVISION_SUMMARY.md` (~8.9 KB)
  - `DOCUMENTATION_INDEX.md` (this file)

---

## Status Summary

### ✅ Completed
- Milestone 1 Setup (FastAPI + Neo4j)
- Data Models (6 tests passing)
- Code Exploration (80-page analysis)
- API Endpoint Tests (21 tests passing)
- Service Layer Tests (15 tests written, RED phase)
- Agent Teams Documented
- Plans Updated with Team Assignments

### ⏳ Ready to Start
- Task #7 GREEN Phase (Service Implementation)
- 3 Parallel Teams with Sonnet 4.5 developers
- 2-3 day timeline
- All prerequisites complete

### ⏳ Pending
- Task #8: API Routers (21 tests)
- Task #9: Code Review (refactoring)
- Milestones 2-7: Frontend + Production

---

## Getting Started

### For New Team Members
1. Read: `REVISION_SUMMARY.md` (what happened today)
2. Read: `AGENT_TEAM_PROGRESS.md` (your role)
3. Read: `~/.claude/plans/immutable-hopping-wall.md` (full context)

### For Starting Implementation
1. Read: `TASK_7_GREEN_PHASE_QUICKSTART.md` (your section)
2. Run: Pre-Implementation Checklist
3. Daily: Report to Tech Lead using standup template

### For Monitoring Progress
1. Use: `TASK_7_MONITORING.md` (daily template)
2. Track: Metrics from `AGENT_TEAM_PROGRESS.md`
3. Report: To Tech Lead → Lead Architect

---

**Documentation Complete & Ready** ✅
**Next Action:** Begin Task #7 GREEN Phase
**Timeline:** 2-3 days for all teams to complete services
