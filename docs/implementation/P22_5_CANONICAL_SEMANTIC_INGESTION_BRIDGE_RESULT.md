# P22.5 — Canonical Semantic Ingestion Bridge — Local Validation Result

Date: 2026-09-19

Status: `LOCAL_VALIDATION_PASS / AWAITING_CANONICAL_INTEGRATION`

Base canonical SHA: `4b4b7390160c16af0ab3b0f2a151b0fbed2edc7e`.

## Purpose

Remediate the P22.5 blocker where real B1 collection produced 28 legacy live-analysis claims but zero canonical P13 semantic claims and zero P13.5 verification decisions.

## Bridge behavior

For the bounded OFAC + White House cohort only:

```text
LIVE_ANALYSIS_CLAIM
  -> P13.1 semantic claim
  -> observed PUBLICATION provenance
  -> UNKNOWN / UNRESOLVED underlying origin
  -> ATTRIBUTION_ONLY evidence
  -> low/unknown multidimensional confidence
  -> P13.5 DETECTED decision
```

Headline text supplies a low-confidence proposition but does **not** define semantic claim identity. Semantic identity is bound to the legacy live-claim identity.

Publisher/source/host counts, official status and legacy confidence do not establish independence or factual verification.

## Validation

Targeted semantic regression on owner node:

```text
50 passed in 80.61s
```

Full exact-worktree owner-local regression:

```text
1358 passed in 617.01s
architecture = aarch64
host = kgm-e4-owner-pilot
```

Real P22.5 observation DB was copied into an isolated test project and bridged:

```text
raw/live claims = 28
canonical semantic claims created = 28
canonical evidence relations = 28 ATTRIBUTION_ONLY
canonical independence assessments = 0
canonical P13.5 decisions = 28 DETECTED
PARTLY_VERIFIED = 0
VERIFIED = 0
integrity_check = ok
```

Idempotency replay:

```text
created = 0
skipped = 28
```

The original P22.5 observation DB and deployed runtime were not mutated.

## Gate status

The semantic-ingestion implementation blocker is locally remediated, but P22.5 is **not yet canonical-validated** because GitHub Actions integration is intentionally deferred under the active Actions quota constraint.

P22.6 remains closed.
