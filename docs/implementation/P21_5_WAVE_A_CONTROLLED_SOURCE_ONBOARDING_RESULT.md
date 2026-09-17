# P21.5 Wave A — Controlled Public/Free Source Onboarding Result

Status: `IMPLEMENTED / VALIDATION_CANDIDATE`

Wave A adds two owner-authorized repository source paths without deploying or restarting the stale `/opt/k-geopolitical-monitor` runtime:

- `ukraine-government-kmu-uk` -> `ukraine.uk.official_government`;
- `suspilne-uk` -> additional `ukraine.uk.national_media` path.

Both are public, free, anonymous HTTPS RSS paths, have deterministic fixtures, P20.5 qualification `ELIGIBLE_NOT_ACTIVE`, explicit P21.5 repository activation, and deterministic adapter-disable rollback. P20.5 itself remains non-activating; activation authority comes only from the recorded P21.5 owner decision.

Fresh owner-local probe at `2026-09-17T02:23:08.192373+00:00`: `2/2 SUCCESS`, `120 items`. `suspilne-uk` was `HEALTHY/FRESH` against its 120-minute expectation. KMU acquisition/parser was healthy but content age was about 464 minutes, so it is retained as `HEALTHY_COLLECTOR / STALE_CONTENT` rather than receiving healthy/fresh adequacy credit.

No independent-origin credit is granted automatically. The KMU origin group identifies the direct institutional publication stream only; an official publication proves what the institution published, not automatically the underlying event claim. Suspilne remains item-level provenance dependent. P13.5/P13.6 remain factual-verification authority.

Gate remains `P21_5_CONTROLLED_SOURCE_ONBOARDING_VALIDATED` pending full CI and formal closure/state sync.
