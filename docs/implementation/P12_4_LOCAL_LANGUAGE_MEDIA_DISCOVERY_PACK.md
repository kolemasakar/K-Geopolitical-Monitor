# P12.4 — Local-Language and Media Discovery Pack

Date: 2026-09-01
State: `VALIDATED`
Gate: `P12_4_LOCAL_LANGUAGE_DISCOVERY_VALIDATED`
Validation anchor: `595d7f0f0e6316e95aca518bb9309e615f239479`
Depends on: P12.1 source portfolio + P12.2 adapter framework + P12.3 authoritative pack closure.

## Objective

Expand public/free discovery into a first explicit local-language media slice without treating publisher count, domain count, language count or translation as independent-origin corroboration or proof of global coverage.

Initial configured language slice:
- `uk` — Ukrainian;
- `ru` — Russian;
- `pl` — Polish;
- `tr` — Turkish.

This is a prioritized first slice only. `GLOBAL` is not implied.

## Source Pack

| Source | Language | Region scope | Role | Endpoint | Validation availability |
| --- | --- | --- | --- | --- | --- |
| Ukrainska Pravda — Ukrainian News | `uk` | Ukraine / Eastern Europe | MEDIA/DISCOVERY | `https://www.pravda.com.ua/rss/view_news/` | `ACTIVE` |
| Meduza — Russian RSS | `ru` | Russia / Eurasia / Eastern Europe | MEDIA/DISCOVERY | `https://meduza.io/rss/all` | `ACTIVE` |
| RMF24 — Polish News | `pl` | Poland / Central Europe | MEDIA/DISCOVERY | `https://www.rmf24.pl/feed` | `ACTIVE` |
| Haberturk — Turkish News | `tr` | Turkey / Black Sea / Middle East | MEDIA/DISCOVERY | `https://www.haberturk.com/rss` | `ACTIVE` |

All four are public-anonymous/free HTTPS inputs. No paid provider or credential is introduced.

## Native Query Probe

Controlled-live validation uses source-specific native query terms instead of assuming semantic equivalence of one English query:
- `uk`: `Україна`;
- `ru`: `Украина`;
- `pl`: `Ukraina`;
- `tr`: `Ukrayna`.

The broad discovery collector itself is bounded and does not require an English watch query to match foreign-language text.

## Original-Language / Translation Boundary

P12.4 preserves original Unicode title/summary and source URL at acquisition.

Adapter metadata records `content_language`, `native_query_term`, `region_scope`, `discovery_role=MEDIA`, `translation_state=ORIGINAL_NOT_TRANSLATED` and language-pack version.

P12.4 does not translate in the adapter. Existing translation functionality remains a separate derived representation and does not create a new source or independent origin.

## Provenance / Truth Boundary

Media publication is not automatically the underlying origin. A media item may derive from the outlet's own reporting, an official statement, a wire service, another publisher, social content or multiple/unresolved origins.

Therefore:
- publisher/domain/language/adapter/item count is not independent-origin count;
- translation does not create independent corroboration;
- feed inclusion does not verify the underlying event;
- reputation/portfolio metadata does not promote claim truth;
- local-language discovery does not change factual confidence by itself.

## Governance / Security

Each source requires an exact P12.1 portfolio record and P12.2-compatible adapter identity/version/HTTPS hostname. Governance is idempotent for exact matches and fails closed on drift instead of silently superseding an approved source definition.

Public-anonymous P12.2 transport constraints remain unchanged. Runtime storage remains `PROJECT_LOCAL_ONLY`; public KGM ingress and production/live activation remain absent.

## Validation

Deterministic fixtures cover all four languages and verify Unicode preservation, language/native-query metadata, governance idempotency/drift rejection, broad-discovery behavior independent of English-query equivalence, source-failure isolation and no translation/verification/independence/coverage promotion.

Evidence:
- x64 CI `33531518780`, job `99935566406`: `370 passed, 1 warning / SUCCESS`;
- native ARM64 `33531518525`, job `99935564828`: `370 passed, 1 warning / SUCCESS`, real `aarch64`, bootstrap/unattended/systemd PASS;
- controlled-live `33531518652`, job `99935565895`: `4 SUCCESS / 0 FAILED`.

See:
- `docs/implementation/P12_4_LOCAL_LANGUAGE_MEDIA_DISCOVERY_PACK_RESULT.md`;
- `docs/implementation/P12_4_CONTROLLED_LIVE_LANGUAGE_SOURCE_MATRIX.md`.

## Explicit Coverage Gap

The first pack covers only `uk/ru/pl/tr`. Other languages, publishers, inaccessible/removed pages, local closed platforms and not-yet-indexed material remain explicit gaps. P12.4 does not claim complete regional or global language coverage.

## Non-Goals

P12.4 does not implement Phase 13 semantic verification, infer independent origin from media/domain/language count, translate inside acquisition adapters, approve paid providers, deploy public API/dashboard/GPT ingress, activate shared runtime or set production/live operational status to operational.
