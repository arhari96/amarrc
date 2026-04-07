# Project State

## Current Phase
**Phase:** 01 - Usage-Based Balance System
**Status:** Planning

## Position in Workflow
- [x] Context created (CONTEXT.md)
- [x] Roadmap created (ROADMAP.md)
- [ ] Plans created
- [ ] Execution
- [ ] Verification

## Key Decisions

### Locked Decisions
None yet - awaiting planning

### the agent's Discretion Areas
1. **Transaction signal implementation** - Use Django signals vs override save() method
2. **Frontend framework choice** - Continue with existing React setup or suggest alternatives
3. **UI component library** - Select appropriate library for modern UI (if frontend work done)

## Pending Todos
- Create PLAN.md files for Phase 01
- Execute backend changes first (mandatory)
- Execute frontend changes second (optional)

## Blockers
None

## Context Summary
User wants to change from:
- **Current:** Manual balance recharge → debit on RC creation → show remaining balance
- **Desired:** Usage tracking (starts 0, increases with RC) + Transaction model (reduces usage) + Limit field (blocks when exceeded)

Key requirements:
1. Rename `balance.balance` to `balance.usage`
2. Add `balance.limit` field
3. Create `Transaction` model with auto-reduce signal
4. Block RC creation when `usage + cost > limit`
5. Admin panel for transaction management
6. (Optional) Modern frontend with usage dashboard

---

*Last updated: 2026-04-07*
