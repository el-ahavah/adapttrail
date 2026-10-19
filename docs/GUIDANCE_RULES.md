# Explained planning guidance: first release

Stage 3 adds deterministic planning prompts in `guidance.py` (`planning-1`), saved under assessment version `preliminary-3-explained`. It uses no AI service and makes no suitability score, irrigation-amount calculation, crop-yield forecast or drought prediction.

## Supported scope

The existing three approaches remain: soil cover, rainwater collection and water monitoring. Only soil-cover assessments recognize exact crop names `maize`, `corn` and `grain maize`, after case and whitespace normalization. Mixed crops, other spellings and all other crops receive an explicit unsupported-crop message. Country and region do not classify crops, soil or suitability. Resource text is context only; structured material availability, budget and upkeep answers drive planning prompts.

Growth choices now include vegetative, flowering, grain filling and ripening, alongside the older unknown, seedling, established and not-applicable choices. An established plant is never inferred to be flowering. Unknown and ambiguous stages produce a request to identify the stage, not a watering prescription.

## Rule map

| Rule | Trigger | Purpose | Basis |
| --- | --- | --- | --- |
| drainage-first | Soil cover + poor drainage | Observe and request drainage assessment before changing cover or watering | FAO soil-water principles |
| sandy-observation | Soil cover + sandy soil | Record moisture changes for local planning | FAO soil-water principles |
| clay-observation | Soil cover + clay, without reported poor drainage | Observe surface water | FAO soil-water principles |
| maize-sensitive-stage | Supported crop + flowering or grain filling, for soil cover | Review supply and soil moisture with local advice | FAO crop-growth guidance |
| maize-stage-check | Supported crop + any other stage, for soil cover | Confirm stage without assuming maturity | FAO crop-growth guidance |
| materials-check | Soil cover + materials absent/unknown | Check material suitability and cost | AdaptTrail planning logic |
| limited-water | Soil cover + low water | Document supply without inferring soil dryness | AdaptTrail planning logic |
| rainwater-quality | Rainwater for food crops or drinking/cooking | Seek water-quality advice before use | CDC guidance |
| budget-plan | Low budget | Identify setup and upkeep costs | AdaptTrail planning logic |
| upkeep-plan | Maintenance unavailable | Arrange support before starting | AdaptTrail planning logic |
| measurement-plan | Water monitoring | Plan comparable baseline records | AdaptTrail recordkeeping logic |
| weather-context | Successfully saved weather snapshot | Check site conditions using forecast context | Saved Open-Meteo data + AdaptTrail planning logic |

Check-first constraints appear before general planning steps. Low water availability does not override reported poor drainage. Unknown values never become favourable conditions. Forecast rain does not cancel soil checks; three dry forecast days do not diagnose drought. Missing weather generates an explicit limitation while preserving other suggestions.

## Sources and review status

Sources checked on 19 October 2026:

- [FAO: Soil and water](https://www.fao.org/4/r4082e/r4082e03.htm), sections 2.2–2.4. Used for general principles only, not numerical application schedules.
- [FAO: Influence of water shortages on yields](https://www.fao.org/4/t7202e/t7202e05.htm), section 2.2 and Table 2. Used for maize stage awareness, not yield estimates or a site-specific water allocation.
- [CDC: Collecting rainwater and your health](https://www.cdc.gov/drinking-water/about/collecting-rainwater-and-your-health-an-overview.html), dated 23 July 2024. General water-quality guidance from the US; local requirements must still be checked.
- [Open-Meteo](https://open-meteo.com/) supplies optional forecast data. Weather-provider attribution and license remain in the weather section. The provider does not author AdaptTrail's suggestions.

Sources inform the explanations; they do not endorse this engine. All suggested actions are AdaptTrail interpretations, not quotations. The displayed reference-check date is not an agronomist approval date. **Local agricultural review and farmer validation remain outstanding.** No named reviewer, independent verification or measured impact is claimed.

Before a real-world pilot of advice, have a local agricultural adviser review crop names, stages, regional applicability and constraint handling. Record the review scope and changes, then run the relevant regression cases. Until then, present this as preliminary planning support.

## Persistence and checklist behavior

Generation runs once when saving a new assessment, after the optional weather request. Each card stores its explanation, triggering answers, source metadata and the corresponding position in the saved check list. Source changes or later project-context edits do not recalculate old results.

New actions append to the check list, retaining the positions of existing basic checks. They use the existing preview, editable title, owner checks and duplicate-import constraint. Completed tasks can use the existing observation flow. Standalone assessments display prompts but do not import them into an arbitrary project. Older assessments without `guidance` still render normally.

No schema migration or new dependency is required. `tests/test_guidance.py` covers recognized/unsupported crops, explicit stages, conflicting constraints, weather presence/absence, action indices and lengths, saved source metadata, legacy results and assessment → task → observation. Hosted verification checks saved maize guidance, attribution, imports and ownership against PostgreSQL.

Stage 4 alerts, background monitoring and external messaging are not included.
