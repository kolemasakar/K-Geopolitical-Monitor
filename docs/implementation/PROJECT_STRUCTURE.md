# PROJECT_STRUCTURE

Initial Minimal Functional Core implementation layout.

```text
src/
  domain/
    entities/
    value_objects/
  ingestion/
  processing/
  verification/
  analysis/
  forecasting/
  reporting/
  storage/
  api/

config/
database/
migrations/
tests/
docs/
```

Principle:
Keep domain logic separated from external integrations and infrastructure.

Status: APPROVED
