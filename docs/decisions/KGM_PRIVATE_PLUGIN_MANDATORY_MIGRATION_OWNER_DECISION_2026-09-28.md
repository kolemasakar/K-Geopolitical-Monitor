# Owner decision — mandatory private Plugin migration — 2026-09-28

Status: OWNER APPROVED DIRECTION; IMPLEMENTATION AND CONNECTIVITY NOT YET ACCEPTED.

## Decision
- KGM must transition fully to a ChatGPT Plugin. The Plugin path is mandatory, not optional.
- Execute all feasible Plugin migration work first, including the private USER package, tool contract, isolated tests, security review, and preparation for registration.
- Investigate and validate the private MCP tunnel **after** completing all migration work that does not depend on an actual hosted connection.
- Maintain FREE-ONLY and owner-only scope; no public publication, public ingress/Funnel, paid relay, cross-project runtime, or unapproved production changes.
- Do not fabricate an MCP endpoint, create an unusable live connector, or claim activation without a verified transport and actual hosted handshake.
- Any network listener, secret provisioning, or production mutation still requires separate explicit authorization under existing security gates.

## Execution order
1. Finish Plugin package and schema/registration readiness using current Plugin Creator contract; expose only sanitized read-only kgm_get_status.
2. Complete independent isolated security and exact-SHA validation; preserve strategic P23.4 gates.
3. Research available private tunnel transport and authentication, costs, and reachability; perform approved synthetic hosted handshake before production activation.
4. Register/activate private USER Plugin when its required real connection and security prerequisites have been met; do not treat preparatory packaging as an activated integration.

## Observed state at decision
- Canonical main: 1d6873e85fb5cb5327a9e8193e5090c815affa38.
- Draft PR #161 head observed: 21e978b129c1705517d7fdfa78e5c2bfcb3d5814.
- Existing focused test evidence: 29 passed, 1 warning at f8b823c5ae499059e16d0f266e3ba371513e8de7, not current-head acceptance.
- Personal owned Plugin listing in this session returned zero plugins.
- No real hosted private transport or production endpoint verified.

This decision supersedes the earlier sequencing preference to research tunnel feasibility before doing any Plugin migration work. It does not waive transport, security, free-only, or owner approval gates.
