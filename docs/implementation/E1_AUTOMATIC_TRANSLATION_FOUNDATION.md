# E1 Automatic Translation Foundation

Status: BASELINE_VALIDATED
Date: 2026-08-29
Project: K-Geopolitical Monitor
Workstream: E1 - unnumbered post-Phase-11 expansion

This workstream does not create ROADMAP Phase 12 or M14.
Production/live remains NOT_OPERATIONAL.
External translation provider remains NONE_APPROVED.

## 1. Purpose

E1 adds a durable provider-neutral translation foundation for source material while preserving original-language content, provenance and verification independence.

Translation is a derived representation. It is not a new source, new evidence origin or factual corroboration.

## 2. Audit Finding

Before E1, M10 provided language registries and TRANSLATION attribution metadata through region/language coverage, but it did not provide:
- durable translated text;
- translation version history;
- provider/method metadata;
- explicit translation result status;
- visible failed/ambiguous translation state;
- retranslation history.

M8 already defined verification independence using the original publisher/origin host derived from live_source_provenance.original_url. E1 preserves that boundary.

## 3. Additive Persistence

Migration:
- migrations/018_translation_foundation.sql

Table:
- raw_item_translations

Persisted fields include:
- translation_id;
- raw_item_id;
- text_field;
- source_language;
- target_language;
- original_text;
- translated_text;
- status;
- method;
- provider;
- provider_version;
- translation_version;
- underlying_origin_id;
- origin_kind;
- uncertainty_note;
- error_message;
- created_at.

Translation history is additive and versioned. Retranslation creates a new version and does not rewrite the original raw item.

## 4. Translation States

Supported states:
- SUCCESS;
- FAILED;
- UNAVAILABLE;
- UNSUPPORTED;
- AMBIGUOUS.

Semantics:
- SUCCESS requires translated text;
- AMBIGUOUS requires translated text plus an explicit uncertainty note;
- FAILED, UNAVAILABLE and UNSUPPORTED retain an explicit error and no translated text;
- degraded translation state is persisted rather than silently dropping the source.

## 5. Provider-Neutral Runtime Contract

Module:
- src/kgeopolitical_monitor/translation_foundation.py

Implemented contracts:
- TranslationAdapter;
- TranslationAdapterResult;
- TranslationRecord;
- TranslationService;
- DeterministicTranslationAdapter for local deterministic validation.

The deterministic adapter is local test/validation infrastructure. It is not an activated external translation provider.

External translation provider status:
- NONE_APPROVED.

## 6. Origin and Truth Isolation

For live items:
- underlying_origin_id is inherited from the normalized original_url host already used by M8 provenance semantics.

For non-live raw items without live provenance:
- source_id is used as the fallback origin identity.

Mandatory invariants:
- raw_items title/content are not rewritten by translation;
- translated text is stored separately;
- translation inherits the source material origin;
- translation never creates a new independent-origin credit;
- translation never increases M8 independent-origin count;
- translation never changes verification state;
- translation does not modify graph, forecast, coverage or reporting truth state.

Conflicting live provenance origins for one raw item fail closed rather than selecting an arbitrary origin.

## 7. Validation

Implementation commits:
- 95ccc5208447f7a144208f10cbf4fbf64411ce00 - Add E1 translation foundation schema
- d60660067e44d5cbbe610a0b74ff50a0f096da4b - Implement provider-neutral E1 translation foundation
- 51bbb41e6edb716760727d06902ac90e8e6ce5c5 - Add E1 translation foundation tests
- 9b5f300b0b798cd106ab84d57d14e01c52b4af62 - Validate E1 translation migration

Canonical E1 code regression:
- GitHub Actions run: 33244484173
- job: 99079456390
- result: SUCCESS
- pytest: 241 passed in 37.10s

Validated behavior:
- original text remains unchanged;
- successful translation persists separately;
- retranslation creates version history;
- live origin host is inherited;
- non-live source identity fallback is explicit;
- SUCCESS/FAILED/UNAVAILABLE/UNSUPPORTED/AMBIGUOUS states persist;
- ambiguity remains visible;
- translation history survives runtime restart;
- M8 independent-origin count and verification state remain unchanged after translation.

## 8. Gate

E1 gate result:
E1_AUTOMATIC_TRANSLATION_FOUNDATION_BASELINE_PASS

State:
- E1: BASELINE_VALIDATED
- runtime storage: PROJECT_LOCAL_ONLY
- external translation provider: NONE_APPROVED
- production/live: NOT_OPERATIONAL
- next workstream: E2 Source Reputation and Status History

E2 remains an unnumbered post-Phase-11 workstream and does not create ROADMAP Phase 12 or M14.
