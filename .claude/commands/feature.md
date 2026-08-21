# /feature — Add Feature to Existing Project

Add this feature: $ARGUMENTS

## Feature Protocol (≤3 turns):

### Turn 1 — Understand Existing Architecture (Parallel)
Read ALL relevant existing code:
- Routes/controllers in the feature domain
- Database schema + models
- Frontend components in relevant section
- Shared types + utilities
- Existing test patterns

### Turn 2 — Implement Complete Feature (Parallel)
Write ALL new code in 1 batch, matching existing patterns:

Backend:
- Route(s) with validation matching existing style
- Business logic in correct layer
- DB migration if schema changes
- Error handling matching project patterns

Frontend:
- Component(s) following existing design system
- API integration with loading/error/success states
- Navigation + routing integration

Tests:
- Unit test for business logic
- API integration test
- Component test

### Turn 3 — Integration Check
Full test suite. Zero broken existing tests. End-to-end verify.

Style: match EXACTLY the existing project's patterns.
Feature complete, tested, integrated.