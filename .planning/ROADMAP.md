# Amarrc Project Roadmap

## Phase 01: Usage-Based Balance System

**Goal:** Transform balance system from manual recharge/debit to usage-based model with transaction tracking and spending limits

**Requirements:** [USAGE-01, USAGE-02, USAGE-03, USAGE-04, USAGE-05, USAGE-06, USAGE-07, ADMIN-01, ADMIN-02, ADMIN-03, FRONT-01, FRONT-02, FRONT-03, FRONT-04, FRONT-05]

**Plans:** 3 plans

Plans:
- [ ] 01-01-PLAN.md — Core backend: Transaction model, Balance model changes, signals
- [ ] 01-02-PLAN.md — API updates: RC creation validation, balance endpoints, admin integration
- [ ] 01-03-PLAN.md — Frontend: Usage dashboard, transaction history, UI improvements (optional)

**Status:** Not started

**Notes:**
- Backend changes are mandatory (USAGE-01 through USAGE-07, ADMIN-01 through ADMIN-03)
- Frontend changes are optional enhancement (FRONT-01 through FRONT-05)
- Existing balance data must be migrated without loss
- Transaction signals must handle edge cases (negative usage prevention)

---

## Future Phases (TBD)

### Phase 02: User Authentication & Authorization
**Goal:** Add user accounts with role-based access control

**Requirements:** []

**Plans:** 0 plans

Plans:

**Status:** Not planned

### Phase 03: RC Search & Filter Enhancements
**Goal:** Advanced search, filtering, and pagination for RC records

**Requirements:** []

**Plans:** 0 plans

Plans:

**Status:** Not planned

---

## Cross-Phase Dependencies

| Phase | Depends On | Provides To |
|-------|------------|-------------|
| 01 | None | 02 (user balance tracking) |
| 02 | 01 | 03 (user-specific RC access) |
| 03 | 02 | - |

---

## Technical Debt & Concerns

- Image generation logic embedded in model `save()` methods (should extract to service layer)
- No test coverage for balance/RC creation logic
- N+1 query potential in balance list endpoint
- Hardcoded font paths in image generation

---

*Last updated: 2026-04-07*
