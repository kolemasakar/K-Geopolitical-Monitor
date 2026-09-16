# P21.3 Operational Coverage Adequacy Baseline v1

Assessed at: `2026-09-16T16:59:49.917696+00:00`

## Global result

| Metric | Count |
|---|---:|
| Target cells | 33 |
| ADEQUATE | 1 |
| THIN | 10 |
| MISSING_EXPECTED_COVERAGE | 21 |
| DEGRADED_COLLECTION | 1 |
| UNKNOWN | 0 |

## Required cells

- ADEQUATE: `1`
- THIN: `5`
- MISSING_EXPECTED_COVERAGE: `21`

## Key findings

- `eu.en.international_organization` is the only current cell that satisfies all approved policy thresholds fail-closed.
- `global.multi.public_osint` is `DEGRADED_COLLECTION` because the fresh GDELT attempt returned HTTP 429.
- Required cells with fewer than the policy minimum are `THIN`; required cells with zero matching governed sources are `MISSING_EXPECTED_COVERAGE`.
- Unresolved origin never creates independence credit; known independent-origin groups are used only as a lower bound.
- Operational adequacy does not alter factual verification; P13.5/P13.6 remain authoritative.

## Cell results

| Cell | Requirement | Criticality | Status | Sources | Healthy |
|---|---|---|---|---:|---:|
| `ukraine.uk.national_media` | REQUIRED | CRITICAL | **THIN** | 1 | 1 |
| `ukraine.uk.official_government` | REQUIRED | CRITICAL | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `russia.ru.national_media` | REQUIRED | HIGH | **THIN** | 1 | 1 |
| `russia.ru.official_government` | REQUIRED | HIGH | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `eu.en.international_organization` | REQUIRED | HIGH | **ADEQUATE** | 3 | 2 |
| `europe.en.official_government` | REQUIRED | STANDARD | **THIN** | 1 | 1 |
| `central_europe.pl.national_media` | REQUIRED | HIGH | **THIN** | 1 | 1 |
| `black_sea.tr.national_media` | REQUIRED | HIGH | **THIN** | 1 | 1 |
| `middle_east.ar.national_media` | REQUIRED | HIGH | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `middle_east.en.international_organization` | OPTIONAL | STANDARD | **THIN** | 0 | 0 |
| `east_asia.zh.national_media` | REQUIRED | HIGH | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `east_asia.ja.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `east_asia.ko.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `southeast_asia.id.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `southeast_asia.en.national_media` | OPTIONAL | STANDARD | **THIN** | 0 | 0 |
| `south_asia.hi.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `south_asia.en.national_media` | OPTIONAL | STANDARD | **THIN** | 0 | 0 |
| `central_asia.ru.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `caucasus.multi.regional_local_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `north_africa.ar.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `north_africa.fr.national_media` | OPTIONAL | STANDARD | **THIN** | 0 | 0 |
| `sub_saharan_africa.en.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `sub_saharan_africa.fr.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `united_states.en.official_government` | REQUIRED | HIGH | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `north_america.en.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `latin_america.es.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `brazil.pt.national_media` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `oceania.en.national_media` | REQUIRED | WATCH | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `global.en.wire_service` | REQUIRED | HIGH | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `global.en.sanctions_regulatory` | REQUIRED | HIGH | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `global.en.economic_energy` | REQUIRED | STANDARD | **MISSING_EXPECTED_COVERAGE** | 0 | 0 |
| `global.en.think_tank_research` | OPTIONAL | WATCH | **THIN** | 0 | 0 |
| `global.multi.public_osint` | OPTIONAL | WATCH | **DEGRADED_COLLECTION** | 1 | 0 |
