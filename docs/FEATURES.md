# AdaptTrail feature reference

Detailed behavior, privacy boundaries and feature migration notes. Paths in code examples are relative to the repository root. For current validation status, see [stage 5](STAGE_5.md).

## Progress tracking (implemented)

Open a private project, save its status as Planned, Ongoing, or Completed, then choose **Track progress**. Add dated observations, a baseline, or follow-up measurements. Measurements require a metric, unit, and period; missing measurements are not zero. History is chronological and private to the owner. Deleting a project also deletes its progress entries after the existing confirmation. Progress entries cannot yet be edited individually, and baseline-to-follow-up comparison is available on the progress page; charts are not yet available.

Local SQLite upgrades automatically. Hosted PostgreSQL requires applying `sql/progress-tracking.sql` before deploying this release. This migration preserves existing drafts and adds the private progress table with backend-only permissions.


## Preliminary suitability checks (implemented)

Choose **Assess this approach** on a Discover story, or **Assess an approach** on your private project. Sign-in is required to save answers. Assessment history is private to its owner and stores the input context, result, timestamp, and rule version. Assessments linked to a project are removed when that project is deleted.

This first engine provides explained planning checks for soil cover, rainwater collection, and water monitoring. It flags unknown information and reported constraints; it does not calculate validated suitability scores. General references are linked in results. Rules are provisional and have not received independent practitioner review. Soil-cover assessments use limited maize growth-stage prompts alongside relevant conditions. Other crop names and free-text resources remain context. Optional Open-Meteo weather snapshots and on-demand project weather notices are integrated. AI is not integrated. The feature remains optional.

Hosted installation requires `sql/suitability-assessments.sql`. Local SQLite adds the table automatically. Assessment snapshots remain private. Community story publication is available separately. Translations, specialist review and background weather monitoring remain future work.


## Community publication (implemented)

Open a private project and choose **Preview publication**. Select the public title, general country, problem, action, reported outcome, and lessons. Preview and explicitly confirm permission before publishing. Discover lists real user stories separately from fictional demos, with a Self-reported label. Assessments, conditions, and progress records are not automatically published. Public snapshots require explicit republishing to update. Unpublishing removes public access while retaining private data; previous visitors may retain copies. Deleting a private project removes its publication and reports.

Visitors can submit reports for operator review. Reports do not automatically hide content. Operators with server access can use `flask --app app review-reports`, `flask --app app moderate-story STORY_ID`, and `flask --app app moderate-story STORY_ID --restore`. A moderation-hidden story cannot be republished by its owner. Review is manual; reports are not automatically sent as notifications. Hosted installations require `sql/community-publication.sql`.


### Private adaptation history

Open a project and select **View adaptation history**. The timeline combines project creation, linked saved assessments, and progress observations in date order. Observation dates are user supplied; creation and assessment dates use UTC. Zero measurements remain visible, and missing measurements are labelled. Assessment links reopen the saved context and rule version.

The source of inspiration, project status, and publication state show their current values. This is not a complete audit log of edits, status changes, or publication events. History is owner-only and is never automatically published. Deleting a project removes its linked history records. No weather feed, verified impact, or causal claim is implied.


### Optional weather context

Assessment forms let users search a town, confirm a named match, and optionally save weather context. Open-Meteo receives the search term and selected town coordinates; no device geolocation is requested. The private assessment saves yesterday's model estimate and a three-day forecast of temperature and precipitation, source attribution, timezone and retrieval time. Reopening an assessment shows its original snapshot, not refreshed weather.

Weather adds conditional planning notes alongside self-reported drainage and growth stage. Soil, crop and resource context remain important; no validated crop-specific thresholds, drought prediction, yield prediction or suitability score is provided. Provider errors, null data and timeouts never turn into fabricated zero measurements; the assessment still saves without weather guidance.

The fixed API endpoints have four-second timeouts, a bounded 15-minute memory cache, and no retries. Open-Meteo's free endpoint is for non-commercial use with rate limits and no uptime guarantee: https://open-meteo.com/en/pricing . No paid subscription or API key is configured. Attribution: Open-Meteo, CC BY 4.0. No schema migration is needed; snapshots use existing assessment JSON storage.


### Adapt community projects

A public community story now offers **Adapt this project**. Signed-in users create a new private project with a reviewed title, their own country, problem, action and conditions, and required notes on what they will change and why. Only the source's public problem and action are suggested; outcomes, lessons, assessments and private progress are not copied.

A separate ancestry record retains the source title and link. Current changes and reasons can be edited from the private project and appear in its private history view. These note edits are not an audit log. The source owner cannot read another person's private adaptation. Publishing remains explicit and shows a public source link while the source is available; adaptation notes are not automatically published.

Unpublished or moderated stories cannot be used to create new adaptations. Existing adaptations remain private and usable after the source is withdrawn or deleted; source deletion clears the foreign key while retaining the title for the adapter's private record. Deleting an adaptation deletes its ancestry record. Hosted setup requires `sql/community-adaptations.sql`; backend-only permissions and RLS match the existing private schema.


### Documented external starter collection

Discover now leads with six editorial summaries from World Bank, FAO and UNEP sources: Tahoua restoration (Niger), Yatenga stone bunds (Burkina Faso), NEWMAP (Nigeria), CALM (Ethiopia), floating gardens (Bangladesh), and Ahmedabad cool roofs (India). `documented_projects.py` stores original-source URLs, publishers, publication dates or explicitly missing dates, check dates, reported outcomes and limitations. Summaries are paraphrased; no source photos or full articles are copied. Local checks and recordkeeping prompts are explicitly AdaptTrail suggestions. These are external examples, not user submissions, expert ratings or endorsements. Historical reporting is not represented as current project performance.

Signed-in users can adapt each example into a private project and edit their changes and reasons. The original source link is retained across project edits and is visible if they explicitly publish a story; private adaptation notes remain private. Existing assessments cover only the three original basic water-related approaches and do not rate external techniques. Old fictional demos remain in a collapsed practice section, preserving their assessment links. No new database migration is required.


### Journey review and pilot preparation

The public **How to use** page explains source labels, privacy, supported assessments, optional weather, progress, history and publication. An anonymous user selecting an adaptation form now returns there after registration and login. Return destinations are restricted to internal GET pages; external URLs and action paths are rejected.

Projects without a supported demo approach now require explicit selection of a supported assessment. External examples never silently default to water monitoring or acquire an unsupported technique rating. Broader suitability rules still need local expert review.

See [the pilot guide](PILOT.md) for an initial task-based usability pilot and feedback questions. The help page does not collect or send feedback, and no pilot invitations or real participant outcomes are included in this change. Do not commit identifiable feedback to this public repository.


### Interface and JavaScript enhancements

The interface uses responsive layouts, a locally served illustrated landscape, forest-green accents, project cards and clearer source labels. A small deferred `static/app.js` adds the mobile navigation toggle, Escape-to-close, search within the current documented/community action filter, empty states, clearing search, and textarea character counts. Account and project submission remain server controlled. No third-party JavaScript or font CDN is added; the existing content security policy stays intact.

Without JavaScript, navigation, server-side action filtering and all project workflows remain available. Animations respect reduced-motion preferences. The optional browser check at `scripts/verify-gui.cjs` requires a separately installed Playwright browser and a running app (`GUI_TEST_URL` defaults to localhost:5055). It checks rendering, search, mobile navigation, overflow and no-JavaScript navigation.

### Personal dashboard

The signed-in workspace at `/drafts` shows project and activity counts, private project cards with suggested next actions, and the five latest saved assessments and progress entries. New accounts receive a welcoming starting point. Counts describe saved activity, not verified outcomes.

Assessment results display preliminary guidance, information gaps, self-reported factor cards, saved weather context and project actions. Reassessment creates a separate snapshot with fresh form answers; it does not replace the saved result.

The project workspace groups the local plan, latest saved assessment, latest progress entry and publication visibility into clear sections. Project status remains self-reported.

The assessment form groups setting, local conditions, resources and optional weather. JavaScript shows approach-relevant planning questions while retaining hidden answers. Without JavaScript, all fields remain available and saving works normally.

Adaptation history uses a responsive timeline with dated project, assessment and observation cards. Optional JavaScript filters show assessments or observations; without JavaScript every record remains visible. Dates retain their existing meaning, and the timeline is not an audit log or evidence of verified impact.

### Baseline and follow-up comparison

The private progress page offers an optional JavaScript comparison of saved baseline and follow-up entries. It requires matching metric and unit labels (ignoring case and surrounding spaces), a follow-up date on or after the baseline, and the user’s confirmation that methods, scope and period durations are comparable. No unit conversions or interpretation of free-text periods are attempted. Missing values remain missing; zero baselines are supported without calculating a percentage. Results show the absolute difference, do not imply causation or verified improvement, and are not stored or published. Changing either selection clears the comparability confirmation. The history and entry form work without JavaScript.

Run comparison checks with `node --test tests/test_progress_comparison.cjs`.

### Private action checklists

Open a project and choose **Open checklist**, or use **Plan next actions** from a project assessment. Add tasks of 1–240 characters, edit them, mark them complete, or reopen them. Archive tasks you no longer need and restore them from the archived section. Counts exclude archived tasks; a completed checklist does not mark the project completed or imply measured impact. Tasks are never included in public story snapshots or copied into another user's adaptation. All mutations require CSRF and project ownership, and individual tasks must belong to the project in the URL. Forms work without JavaScript. Deleting the project also removes its tasks after the existing confirmation.

For a hosted installation apply `sql/project-tasks.sql` before deploying this feature. It uses the existing private schema and backend-only database role; Flask enforces account ownership. Local SQLite creates the table automatically.

### Checklist interaction design

The checklist uses a dedicated JavaScript enhancement and theme-aware stylesheet. Users can filter by completion, search active task titles, and sort by age or incomplete tasks first. Search and sorting only change the current view. Task starters fill an empty composer without submitting; Ctrl/Cmd+Enter submits through the normal validated form. A completion ring reflects all active tasks, independent of filters, with reduced-motion support. Submission feedback preserves the submitted action and resets when navigating back. All task mutations still use server-rendered forms, CSRF validation and ownership checks; the core checklist remains usable without JavaScript.

### Turn saved guidance into actions

Project assessments offer **Add to my checklist** beside each saved local check. The link opens a preview; no task is saved until the owner submits it. Edit the description (1–240 characters), review the original check, then save. Tasks link back to the saved assessment, even after editing, completion or archiving. Duplicate protection is scoped to the project, saved assessment and check position; a database unique index handles repeated or concurrent submissions. Existing completed/archived tasks are preserved and linked instead of replaced. A new assessment is a new snapshot and may provide a separate task. Standalone assessments must first be associated with a project through the existing project assessment flow; they cannot be imported into an arbitrary project.

Hosted setup: apply `sql/assessment-checklist.sql` before deploying. Existing tasks are preserved with empty source fields. Sources are assigned server-side after validating both assessment and project ownership. Preview forms work without JavaScript; optional JavaScript adds save feedback. These private tasks are not automatically published.

### Record what happened after a task

Completed tasks offer **Record what happened**, opening the progress form with the task shown as context. Add an observation, difficulties, or an optional baseline/follow-up measurement. Saving uses the same validation and CSRF protections as ordinary progress entries. The task must belong to the signed-in owner and the current project and still be completed at save time. A reopened or missing task is rejected; unrelated entries remain available from **Track progress**.

Each linked entry stores the task ID and its title at recording time. Renaming, reopening or archiving the task does not rewrite previous observations. Progress history and the adaptation timeline link back to the task. Checklist cards show the linked observation count and a link to the latest saved entry. Multiple observations per task are allowed. These records do not establish causation or verified impact and are not automatically published.

Hosted setup: apply `sql/task-observations.sql` before deploying. Existing entries retain empty source fields. Local SQLite upgrades automatically. Mobile visual verification remains separate from automated workflow tests.


### Reusable project information (stage 2)

Open a private project and select **Manage project information**. Save crop or plants, general region, resources, and structured soil, drainage, growth stage, water and upkeep answers. Unknown answers are allowed. Country stays in the existing draft editor; no exact address is required. Each project has its own details, so different sites or growing seasons need not share assumptions.

New project assessment forms prefill these details. Review them as conditions change. Editing an assessment does not update the reusable information, and updating project information does not rewrite old assessment snapshots. Standalone assessments remain independent. Weather locations are still explicitly selected for each assessment rather than reused automatically. Stage 3 now adds limited maize planning prompts to soil-cover assessments; other crops and resource notes remain context.

Details are owner-only and excluded from automatic publication. Clear a text field or choose Unknown and save to remove a detail from the reusable record. Previous assessment snapshots retain their original answers; deleting the project removes both the project information and its assessment history.

Apply `sql/project-context.sql` before deploying this release. It adds a default-empty text JSON column to the existing private drafts table and retains its backend grants and RLS. SQLite upgrades on connection. No new external service or dependency is introduced. Tests in `tests/test_project_context.py` cover reuse, validation, ownership, escaping, publication privacy, unchanged snapshots, weather-search edits and existing-database upgrades. Hosted smoke verification exercises PostgreSQL persistence and isolation. The stage 3 release below builds on this information.


### Explained guidance (stage 3, initial release)

New assessments show **Suggested next steps for your conditions**: an action, explanation, the answers that triggered it, source links where applicable, and explicit limitations. Soil-cover assessments include limited maize growth-stage prompts; general soil, resource, water-quality and saved-weather checks support the existing approaches. Users can add suggestions to their private checklist and record observations after completing tasks.

This is transparent rule-based planning support, not a validated agricultural recommendation or an AI prediction. Other crops are explicitly unsupported for crop-specific guidance. No irrigation doses, suitability scores or expected yield gains are calculated. Local agricultural review and farmer validation remain outstanding.

See [the rule map, sources and review requirements](GUIDANCE_RULES.md). Old assessment snapshots retain their original wording and source metadata; new rules only apply to new assessments. No database migration or paid dependency is needed. Stage 4 now adds on-demand in-app weather notices; background alerts and external messaging remain future work.


### Weather notices (stage 4, initial release)

Open a private project → **Open weather notices**. Confirm a town, choose reminder preferences, save, then press **Check weather now**. The page shows forecast precipitation, a three-day no-precipitation reminder, and/or a user-selected temperature limit, with dates and practical planning prompts.

This version checks weather only on request. It sends no SMS, email or push messages and does not monitor while the user is away. It does not issue official hazard warnings or diagnose drought. Outdated or failed checks and changed project conditions require refresh; old forecasts are clearly separated as reference only. Turning off notices removes their saved settings and latest weather check.

Apply `sql/weather-notices.sql` before deployment. See [weather notice behavior, privacy and testing](WEATHER_NOTICES.md). No paid dependency was added. Stage 5 adds accessibility and low-data improvements described below.



### Accessibility and low-data access (stage 5)

Use **Accessibility & data use** in the footer to choose standard or low-data mode.
Low-data mode omits the homepage illustration and general enhancement script;
navigation stays visible and native project forms remain usable. The preference
is saved in this browser and overrides its Save-Data hint. An internet connection
is still required; this is not offline saving, SMS or USSD access.

The interface includes larger touch controls, narrow-screen wrapping, a focusable
skip-link destination, keyboard-scrollable weather tables, associated character
counters and error focus. Browser printing uses a simplified reading layout.
The checklist page title has also been corrected for tabs and assistive readers.

Verification on 21 October 2026: 71 Python tests and 6 JavaScript comparison tests
passed. Native assessment → task → observation forms were exercised in standard
and low-data modes. Hosted verification passed against the production database,
including secure preference cookies, low-data authenticated workflows and cleanup.
Live desktop browser checks confirmed mode switching, omitted assets, skip-link
focus and theme switching. No database migration or paid dependency was added.

Stage 5 is implemented and deployed, with automated and desktop checks complete;
mobile viewport, real-device, screen-reader and print-output validation remain
open. See [the stage 5 verification record](STAGE_5.md) for the exact scope
and remaining checks. Stage 6 has not started.
