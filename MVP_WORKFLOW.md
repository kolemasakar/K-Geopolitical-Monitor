# MVP_WORKFLOW
Minimal Functional Core processing workflow.

Version: 0.1
Status: APPROVED

## Processing Pipeline

```text
Source
↓
Discovery
↓
Raw Item
↓
Claim Extraction
↓
Evidence Processing
↓
Event Construction
↓
Deduplication
↓
Storyline Linking
↓
Importance Scoring
↓
Forecasting
↓
Report Generation
```

## First Validation Goal

Verify that one complete information lifecycle works correctly.

The MVP does not target global coverage.

## Required Test Cases

- new event detection;
- duplicate detection;
- conflicting claims;
- event update;
- user provided information;
- forecast update after new evidence.
