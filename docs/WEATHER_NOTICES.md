# Stage 4: private in-app weather notices

This release adds **Open weather notices** to each private project. It is an on-demand forecast reminder service, not background monitoring or an official warning feed. Users must visit the page and press **Check weather now**. No SMS, email, push notification, scheduler or paid service is introduced.

## User journey

1. Search for a town and select the correct match. Searching alone does not enable notices.
2. Choose precipitation, a three-day no-precipitation reminder, and/or a temperature reminder with a user-entered Celsius limit. Confirm consent and save.
3. Press **Check weather now**. The existing Open-Meteo integration validates dates, units and finite values before generation.
4. Review dates, reasons, next steps, source attribution and retrieval time. Reminders use the project conditions saved at the time of checking. Changing project conditions requires another check.
5. Turn off notices to remove their saved location, preferences and latest snapshot. Earlier assessment snapshots are separate and remain unchanged.

## Rules and boundaries

- Precipitation: at least one of the three forecast days has precipitation greater than zero. This includes rain, showers and snow, not only rainfall. It is not a flood or heavy-rain warning.
- No precipitation: all three days have zero forecast precipitation. This does not diagnose drought, soil dryness or a need to irrigate.
- Temperature: the daily maximum reaches or exceeds a limit selected by the user. There is no default crop-damage or health threshold. Values must be finite and between -60 and 60 °C; those are form bounds, not safety limits.
- A no-match result means none of the selected reminder conditions matched, not that the site is safe.
- Poor drainage changes the precipitation reminder's next step to checking standing water and seeking local drainage advice. Other next steps reuse the project's preliminary planning approach; they do not calculate irrigation doses.

Forecast data comes from [Open-Meteo](https://open-meteo.com/en/docs), with [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) attribution. Its daily maximum/minimum temperatures and precipitation totals are model data, not farm measurements. Documentation and [usage terms](https://open-meteo.com/en/terms) checked 20 October 2026. The non-commercial free endpoint has usage limits and no availability guarantee; scaling or monetization requires reviewing the terms again. No subscription was created.

## Freshness and failure behavior

The saved retrieval time is preserved, including when the existing 15-minute provider cache supplies data. The UI suppresses current reminder cards once the snapshot is six hours old, at the location's next midnight, after project context changes, or after a failed refresh. Six hours is an application display policy, not a claim of forecast validity.

A failed refresh retains any earlier forecast in a collapsed reference-only section and shows an error. Missing data is never converted to zero. Saving new preferences or a new location invalidates the previous snapshot. Only the latest successful check is kept; this is not a forecast history archive.

GET requests perform no weather fetch or database update. POST requests require project ownership and CSRF protection and are rate-limited in production. Search results are scoped to the current project in the session. Coordinates cannot be supplied directly by a forged form. Conditional database writes prevent an in-flight refresh from undoing a concurrent disable or preferences update.

## Storage and deployment

Apply `sql/weather-notices.sql` before deployment. It adds `drafts.weather_watch`, a default-empty JSON text column under the existing private schema and access model. No new public grants, RLS policies or tables are needed. SQLite upgrades automatically. Publication continues to use explicit public fields and does not expose the selected town, preferences, conditions or forecast.

`tests/test_weather_notices.py` covers preferences, boundaries, local dates, age, weather outages, context changes, concurrent writes, login return paths, ownership, publication privacy, escaping and SQLite upgrades. The hosted smoke check uses a clearly synthetic forecast to verify database persistence independently of provider availability; the existing optional live-provider check remains separate. Mobile visual testing is still outstanding.

Future background alerts require a separately designed schedule, delivery consent, deduplication, operational monitoring and a cost review. Stage 5 accessibility work is not part of this release.
