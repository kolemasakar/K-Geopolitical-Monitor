# DATA_CONTRACTS
Minimal Functional Core data contracts.

Version: 0.1
Status: APPROVED

## Contract Principles

- provenance must be preserved;
- facts and analysis must remain separated;
- updates must not overwrite history;
- confidence and verification are separate attributes.

## Event Contract

An Event must contain:

- identity
- participants
- chronology
- evidence links
- verification state
- importance assessment
- related storyline references

## Forecast Contract

A Forecast must contain:

- forecast_id
- target process
- time horizon
- scenarios
- probabilities
- confidence
- drivers
- constraints
- triggers
- invalidation signals

## User Provided Data Contract

Required:

- origin_type
- user_reliability_level
- received_time
- verification_state

User reliability must never be silently converted into system verification.
