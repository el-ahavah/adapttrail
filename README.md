# AdaptTrail

**A Green Code, Green Planet initiative.**

**A shared memory of climate action: discover an experience, assess its fit, adapt it locally, measure what happens, and share the lessons.**

## Project status

AdaptTrail is a deployed Flask application with accounts, private projects, preliminary assessments, optional weather snapshots, assessment-linked checklists, task-linked observations, measurement comparisons, adaptation history, and explicit community publication. It uses SQLite locally and PostgreSQL for hosted storage. Discover includes six sourced external examples and three labelled fictional demonstrations. No partnerships, UN affiliation, verified impact, or worldwide originality are claimed.

See the [stage 1 review](docs/PLATFORM_REVIEW.md) for the verified feature inventory, limitations, test results, and proposed next stage.

## The idea

AdaptTrail will help communities find climate adaptation experiences from other places, understand the evidence behind them, and document their own adaptations. Green Code, Green Planet is the broader initiative behind the platform.

The platform will begin with water conservation. Users will explore what others tried, the conditions they faced, the resources they needed, and the results they reported—including unsuccessful attempts. The broader vision includes agriculture, heat resilience, flood preparedness, and ecosystem restoration. Each additional area will require its own relevant data and reviewed guidance.

The intended point of difference is connecting related attempts into a traceable history: where an idea began, how another community changed it, and what happened under different conditions. Matching will consider relevant conditions rather than country alone. This direction still requires comparison with existing platforms and conversations with potential users.

## Optional suitability guidance

The core journey is **Discover → Assess → Adapt → Track → Share**.

Users can browse climate solutions without providing a location or completing an assessment. When they want help deciding whether an approach fits, they can choose **“Help me assess this approach.”** Location and weather are supporting factors alongside their goals, soil, crops, resources, and other relevant conditions.

The following table describes the intended assessment scope, not a claim that every factor already drives advice. The current form saves crop and resource notes as context; preliminary rules support only rainwater collection, soil cover, and water monitoring. See the stage 1 review for the implemented behavior.

The intended assessment considers factors relevant to the selected action:

| Factor | Information considered |
| --- | --- |
| Goal and setting | The water problem, intended use, and scale of the project. |
| Location and climate | General location, seasonal patterns, recent weather, and forecasts where available. |
| Soil and moisture | Soil type, drainage, and user observations of current moisture. |
| Crops and growth stage | Plant type and whether plants are seedlings or established, when relevant. |
| Land and infrastructure | Slope, shade, available space, storage, and existing equipment. |
| Water | Source, reliability, availability, and known quality concerns. |
| Resources | Budget, local materials, skills, and maintenance time. |
| Local guidance | Relevant documented restrictions and practitioner guidance. |

The platform should explain why an option may fit, possible adjustments, missing information, and what to check before proceeding. It must distinguish user observations from external data and show sources, dates, and uncertainty. Forecasts describe possible future weather; they are not direct measurements at the user's site.

The current assessment uses a small set of transparent preliminary rules for selected water-conservation approaches. These rules are not expert-validated. Optional Open-Meteo weather snapshots are implemented; they are not crop-specific predictions. If weather data is unavailable, browsing and project tracking still work; the assessment identifies the gap.

AI may later help explain guidance in everyday language. It must not invent measurements or evidence, and a suitability assessment does not guarantee an outcome.

## Who it is for

- Community groups documenting local water projects.
- Schools and youth groups running practical conservation initiatives.
- Farmers and local organisations exploring relevant experiences.
- Researchers and practitioners who may later help review evidence.

The platform is intended for international use. A first pilot can take place in one community while the product supports countries, currencies, measurement units, and environmental conditions explicitly.

## Example user journey

The following is fictional and illustrates the intended experience, not a completed project or proven result.

1. A school wants to reduce water use in its garden.
2. It searches for experiences with similar rainfall, water sources, and budgets.
3. It reads a case study describing an approach, its costs, measurements, difficulties, and limitations.
4. It optionally asks for a suitability assessment, adds relevant soil, plant, water, and resource details, and reviews the explanation and missing information.
5. It starts an adaptation linked to that case study and explains its changes.
6. It records its starting water use and follows progress over a defined period.
7. It publishes its results, measurement method, and lessons so another group can learn from them.

A favourable result is evidence to examine, not a guarantee that the approach will work elsewhere.

## What the platform will look like

| Area | Purpose |
| --- | --- |
| Discover | Browse experiences and filter by problem and conditions. |
| Case study | Read the action, context, costs, outcomes, limitations, and supporting evidence. |
| Assess suitability | Optional guidance on fit, adjustments, missing information, and checks before trying an approach. |
| My projects | Manage a community's own projects and adaptations. |
| Progress | Record dated observations and compare measurements with a starting baseline. |
| Adaptation history | Follow links between an original experience and subsequent adaptations. |
| Evidence | Show whether a claim is self-reported, supported by submitted records, or reviewed. |

A map can complement search in a later release. The interface should work well on phones and slow connections.

## MVP: first working release

The MVP should demonstrate the complete learning journey, rather than only a submission form.

### Accounts and ownership

Users can register, sign in, and manage their own submissions. Editing another user's project must be prevented. Passwords must be hashed; private information must not appear in public project pages.

### Discover experiences

Users can browse published water-conservation projects and filter by action type, climate category, and water source. Cost records must retain their currency; costs in different currencies must not be ranked as equivalent without a documented conversion.

### Assess an approach

Offer an optional short questionnaire tailored to a selected approach. Use documented rules to show relevant conditions, possible adjustments, and unanswered questions. Retain the assessment date and rule version so guidance can be understood later. Users can skip this step.

### Document a project

A project records:

- Title, country, and general location.
- Water problem and relevant local conditions.
- Action taken, materials, and approximate cost with currency.
- Start date, status, and measurement period.
- Starting measurement, follow-up measurements, units, and collection method.
- Reported outcome, difficulties, and what the contributor would change.
- Evidence references and their source.

Precise personal locations are optional and should not be required for publication.

### Adapt an existing experience

Users can create a new project linked to an existing case study. They describe what they changed and why. The original record remains separate and attributable.

### Record and compare results

Users can add dated observations. Comparisons require compatible units and measurement periods. Missing measurements are shown as missing, not treated as zero. Before-and-after differences must not be presented as proof that an intervention caused the change.

### Publish responsibly

Users choose when to publish. Submissions begin as self-reported. Evidence links do not automatically establish independent verification. The MVP includes a way to report problematic content and a basic owner-operated moderation process.

### Starting content and data sources

Begin with a small curated collection of real water-conservation case studies whose reuse terms permit inclusion. Keep attribution, source links, publication dates, and limitations. Six attributed external summaries are now included; they are not AdaptTrail pilot outcomes.

Use three clearly labelled fictional examples to demonstrate the journey, kept separate from real submissions and impact totals. Invite a few consenting pilot contributors before expanding public participation.

Project stories come from attributed external case studies and user submissions. Featured projects are selected for relevance and clear documentation; featuring is not verification. Adaptation history comes from actual links between an original project and a user's new attempt. Never fabricate these links.

Users can keep an adaptation journal private and publish when ready, allowing the platform to be useful before a large community forms.

## Evidence and trust

The planned evidence labels are:

| Label | Meaning |
| --- | --- |
| Self-reported | A contributor describes an experience; no independent review is implied. |
| Supporting records submitted | Measurement records or references are attached; their presence alone does not validate the claim. |
| Reviewed | A named reviewer has checked a stated scope using a documented method. This requires a future review workflow. |

Record failures and mixed results alongside successes. Preserve attribution and explain uncertainty. Obtain permission before publishing another community's information.

The platform shares experiences; it does not certify engineering designs or drinking-water safety.

## Future development

These features are outside the first release:

- Richer, locally reviewed suitability guidance beyond the implemented optional weather snapshots.
- Map-based discovery as an optional browsing aid.
- Team workspaces and structured practitioner review.
- Multilingual content and translation with access to the original text.
- AI summaries and explained suggestions linked to supporting records.
- Low-connectivity draft capture and later synchronisation.
- Expansion to other adaptation challenges after validating water conservation.

AI must not invent evidence, mark claims as verified, or promise outcomes. Paid AI services are not required for the MVP.

## Technology and budget

Python and Flask power the application, with JavaScript for optional interface enhancements. GitHub holds the code and development history. Render hosts the application, and Supabase PostgreSQL stores hosted records. Accounts are managed by Flask, not Supabase Auth.

The project aims to operate within free service allowances without paid AI dependencies. Provider limits and pricing must be checked before changing service usage; this document does not guarantee ongoing free capacity. The existing provider address avoids requiring a custom domain.

## How we will measure progress

Initial product measures:

- Whether users can complete the discover → assess (optional) → adapt → track → share journey.
- Number of real submissions with clearly described measurement methods.
- Number of adaptations linked to earlier experiences.
- Whether pilot users find the information useful and understandable.

Environmental outcomes should be reported only when supported by real measurements, with the measurement period and limitations stated. Do not count fictional examples as impact or add up incomparable outcomes.

## Relationship to the Global Goals

The intended focus aligns with water conservation and climate adaptation, particularly SDG 6 (Clean Water and Sanitation) and SDG 13 (Climate Action). Cross-community learning may also support SDG 17 (Partnerships for the Goals).

This is an independent initiative. Alignment with the Global Goals does not imply UN endorsement or partnership. Any forum submission should distinguish proposed features, implemented features, and documented results.

## Development milestones

1. Review this concept and interview potential contributors.
2. Compare existing platforms, collect reusable case studies, and refine the project's point of difference.

3. Create the GitHub repository and build the core user journey.
4. Add and review the initial suitability rules; test accounts, permissions, persistent records, comparisons, assessments, and publication.
5. Deploy a demonstration with clearly labelled sample content.
6. Pilot with consenting contributors, learn from feedback, and improve.

## Running the project

Requires Python 3.10 or newer. From the repository directory:

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows PowerShell (use this instead)
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
flask --app app run --debug
```

Open http://127.0.0.1:5000 in your browser. The development server is for local use only.

### Current files

- `app.py`: Python routes and three fictional demonstration records.
- `templates/`: HTML pages rendered by Flask.
- `static/style.css`: responsive styling.
- `requirements.txt`: pinned direct application dependency.

The demonstration collection remains separate from user drafts. Create a draft through **My drafts → Create a draft**. Drafts are stored in `instance/drafts.sqlite3` and persist after restarting. They can optionally reference a fictional demo as inspiration. Open a saved draft and choose **Edit draft** to update it, or **Delete draft** to review a confirmation page. Deletion requires an explicit confirmation and cannot be undone. Progress observations and explicit publication are implemented; private notes are not automatically published.

For local development, create an account with a username and a password of 8–128 characters, then sign in. Each account can access only its own drafts. Passwords are hashed and state-changing forms require CSRF tokens. Use the loopback development server locally. Production configuration enables secure cookies and basic authentication rate limiting and requires production secrets and a PostgreSQL connection. Password recovery is not implemented. Weather is optional; core recordkeeping works without a weather request.

The `instance/` directory and its session key are excluded from Git. To back up local drafts, stop the app and copy `instance/drafts.sqlite3` to a safe private location.

Run the persistence and form checks:

```bash
python -m unittest discover -s tests -v
node --test tests/test_progress_comparison.cjs
```

## Licence

A code licence has not yet been selected. Contributor consent and reuse terms for community submissions must be addressed separately from the software licence.


## Existing drafts from before accounts

The database migration preserves older drafts with no owner. They are hidden from every account and are never automatically assigned to the first person who registers. After creating your account, the owner of the local installation can stop the server and explicitly assign all unowned drafts:

```bash
flask --app app assign-legacy-drafts YOUR_USERNAME
```

Use this only for drafts you own. It leaves already assigned drafts unchanged. Back up the SQLite file before migration or reassignment.


## Hosted deployment preparation

`render.yaml` defines a Free Render web service and an external PostgreSQL database connection. There is no Render database trial in this configuration. Hosted deployment and database workflows were verified in the previous release. The stage 1 review reruns local automated checks; it does not constitute a new live deployment verification.

1. Create a dedicated Supabase Free project for AdaptTrail.
2. Apply `sql/hosted-schema.sql` to that project's SQL editor. Tables are stored in `adapttrail_private`, outside the exposed Data API. Do not expose this schema. The backend uses the dedicated application role; Flask enforces draft ownership. Follow the subsequent role, RLS, and feature migrations in `sql/` as well; this initial schema alone does not install every current feature. These accounts use Flask authentication, not Supabase Auth.
3. In Supabase's **Connect** dialog, copy the **Session pooler** connection string and insert the database password, percent-encoding reserved characters. Set this privately as `DATABASE_URL` in Render. Never commit it or paste it into public messages.
4. Render's Blueprint generates `SECRET_KEY` and sets `APP_ENV=production`. Missing production settings stop startup instead of falling back to disposable SQLite storage.
5. Deploy and verify registration, ownership isolation, restart persistence, and `/health` against the real database before inviting users.

Local accounts and drafts are not automatically copied to the hosted database. Back them up before any future import. A free provider URL can be used initially; no custom domain is required.

Production enables secure cookies, response security headers, and a basic sign-in/registration rate limit. The initial service uses one Gunicorn worker. Rate-limit counters are process-local and reset on restart; shared counters and trusted proxy-aware client addressing are future improvements. Password recovery and account deletion are still pending.

For exports, use Supabase's database backup/export tooling; keep exported account hashes and draft data private. After hosted schema or application changes, verify affected PostgreSQL workflows again. Local SQLite tests do not substitute for that check.


## Progress tracking (implemented)

Open a private project, save its status as Planned, Ongoing, or Completed, then choose **Track progress**. Add dated observations, a baseline, or follow-up measurements. Measurements require a metric, unit, and period; missing measurements are not zero. History is chronological and private to the owner. Deleting a project also deletes its progress entries after the existing confirmation. Progress entries cannot yet be edited individually, and baseline-to-follow-up comparison is available on the progress page; charts are not yet available.

Local SQLite upgrades automatically. Hosted PostgreSQL requires applying `sql/progress-tracking.sql` before deploying this release. This migration preserves existing drafts and adds the private progress table with backend-only permissions.


## Preliminary suitability checks (implemented)

Choose **Assess this approach** on a Discover story, or **Assess an approach** on your private project. Sign-in is required to save answers. Assessment history is private to its owner and stores the input context, result, timestamp, and rule version. Assessments linked to a project are removed when that project is deleted.

This first engine provides explained planning checks for soil cover, rainwater collection, and water monitoring. It flags unknown information and reported constraints; it does not calculate validated suitability scores. General references are linked in results. Rules are provisional and have not received independent practitioner review. Location, crop, and resources are recorded as context rather than used for unsupported local predictions. No weather API or AI is integrated. The feature remains optional.

Hosted installation requires `sql/suitability-assessments.sql`. Local SQLite adds the table automatically. Public sharing, translations, specialist review, and automatic weather context remain future work.


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

See [the pilot guide](docs/PILOT.md) for an initial task-based usability pilot and feedback questions. The help page does not collect or send feedback, and no pilot invitations or real participant outcomes are included in this change. Do not commit identifiable feedback to this public repository.


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
