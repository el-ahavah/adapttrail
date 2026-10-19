# Stage 1: existing platform review

Reviewed 19 October 2026 against main commit `361830ecd3533d9ca9665e248a10fa58e0d845e7`.
Scope: inspect the existing assessment, weather, checklist, and progress journey before building new farmer guidance. Local source files matched the remote commit before edits. This review changes documentation only.

## What already works

| Area | Existing behavior and source | Limit before expansion |
| --- | --- | --- |
| Assessment | `assessment.py`, `app.py:assess_approach`, `templates/assess.html`: three supported approaches, unknown answers, saved inputs and versioned results | Preliminary checks, not a validated suitability score. External case studies are not assessed as complete techniques. |
| Farmer context | Crop, region and resources are saved as optional text; soil, drainage, growth, water, budget and maintenance have structured choices | No reusable farmer profile. Crop and resource text do not drive advice. Several structured fields identify missing information without producing differentiated advice. |
| Weather | `weather.py`: explicit town selection, one recent model-estimate day and three forecast days; source, timezone and retrieval time retained | Saved snapshot, not live monitoring. No drought model, crop thresholds, scheduled alerts or notification delivery. |
| Weather resilience | Bounded cache, request timeout, response validation, unavailable-weather fallback | Tests mock provider data; this review does not verify current provider availability or terms. |
| Checklist | `app.py:task_from_assessment`, `project_tasks`, `update_project_task`: owner-scoped tasks, edit, complete/reopen, archive/restore, assessment provenance and duplicate-import protection | Only saved assessment checks can be imported; weather notes are separate. Completion does not establish success or change project status automatically. |
| Progress | `app.py:project_progress`: observations and optional baseline/follow-up measurements; completed-task links retain the original task title | Self-reported records; no independent review or causal attribution. Measurement methods are not separate structured fields. |
| Comparison | `static/progress-comparison.js`: compatible metrics/units, date order and explicit period/method/scope confirmation; zero stays valid | Absolute difference only; no automatic unit conversion or saved comparison report. |
| Privacy | Owner checks, CSRF, private task/progress records and separate consent-based publication | Not a full security audit; no password recovery or account deletion workflow. |

The existing journey is connected: project assessment → selected check → checklist task → completed task → observation → private history. Reuse these links in future work.

## Verification performed

- `python -m unittest discover -s tests -q`: 41 tests passed.
- `node --test tests/test_progress_comparison.cjs`: 6 tests passed.
- Assessment storage, unknown answers and ownership: `tests/test_drafts.py`.
- Weather selection, snapshots, missing data and outage fallback: `tests/test_weather.py`.
- Explicit supported-approach selection for external projects: `tests/test_journey.py`.
- Assessment-to-task ownership, source validation and duplicate imports: `tests/test_suggested_tasks.py`.
- Task-to-observation persistence, snapshots, isolation and publication privacy: `tests/test_task_observations.py`.

These are local automated checks, not a new production database check, mobile visual test, agricultural validation, or farmer pilot. Mobile visual testing remains outstanding. Passing tests covers these exercised cases, not every possible failure.

## Findings and priorities

1. **Correct outdated documentation now.** The README described deployed features as planned and expert review as if already part of the rules. Update it to distinguish implemented behavior from ambition.
2. **Next proposed stage: reusable project/farm context.** Extend the existing inputs instead of adding a second questionnaire. Keep unknown answers and optional location. Decide how context is edited and reused while preserving old assessment snapshots. Do not silently infer soil or crop from location.
3. **Then improve guidance.** Select a narrow initial crop/use case and have agricultural guidance reviewed. Explain which inputs affect each recommendation, its sources, missing information and limits. Keep unsupported cases explicit. Preserve links into the existing checklist and observation journey.
4. **Later add alert delivery.** Define freshness, location timezone, source failure behavior and user notification preferences before scheduled alerts. A short forecast alone cannot support a drought claim.
5. **Validate accessibility and usefulness.** Complete mobile checks and the usability pilot in `docs/PILOT.md`; later test low-data access and locally reviewed language support. SMS/USSD need separate delivery arrangements.
6. **Measure actual outcomes.** Reuse baseline and follow-up entries with clearly described methods. Crop-yield improvements, insurance protection, farmer reach and reduced displacement are not established by this code or its tests.

## Stage boundary

Stage 1 is complete with this inventory, passing regression checks and documentation corrections. No new profile, advice engine, alerts, messaging integration or database migration is implemented here. Stage 2 awaits the project owner's instruction, as requested.
