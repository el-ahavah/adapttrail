# AdaptTrail

**A Green Code, Green Planet initiative.**

**A shared memory of climate action: discover an experience, assess its fit, adapt it locally, measure what happens, and share the lessons.**

## Project status

AdaptTrail is a deployed Flask application with accounts, private projects, preliminary assessments, optional weather snapshots, on-demand weather notices, low-data display preferences, assessment-linked checklists, task-linked observations, measurement comparisons, adaptation history, and explicit community publication. It uses SQLite locally and PostgreSQL for hosted storage. Discover includes six sourced external examples and three labelled fictional demonstrations. No partnerships, UN affiliation, verified impact, or worldwide originality are claimed.

**Stage 5 is implemented and deployed; full sign-off is pending.** Automated and limited desktop checks passed on 21 October 2026. Mobile, screen-reader, slow-connection and print checks remain open. Stage 6's farmer pilot has not started. See the [stage 5 verification record](docs/STAGE_5.md). The [stage 1 review](docs/PLATFORM_REVIEW.md) is a historical baseline.

## Purpose and audience

AdaptTrail helps farmers, community groups, schools and local organisations learn from climate adaptation experiences and document their own attempts. Green Code, Green Planet is the broader initiative.

The learning journey is **Discover → Assess (optional) → Adapt → Track → Share**. Location supports decisions alongside soil, crops, growth stage, water, resources and local knowledge. The platform is intended for use across countries, with an initial pilot still to be organised.

The starter collection covers land restoration, farming, water and urban heat. Preliminary assessment rules currently cover only **soil cover, rainwater collection and water monitoring**; they do not rate every technique in the collection.

## What works today

| Area | Available behavior |
| --- | --- |
| Discover | Six attributed external summaries, separately labelled fictional demos, published community stories, action filtering and optional text search. |
| Private projects | Account-owned drafts, source links, adaptation notes, project status and reusable local conditions. |
| Assessments | Saved answers, rule versions, explanations, missing information and limited maize planning prompts for soil cover. |
| Weather | Optional Open-Meteo assessment snapshots and project notices refreshed with **Check weather now**. |
| Checklists | Add or import an assessment check, edit, complete, reopen, archive and restore tasks. |
| Progress | Dated observations, optional measurements, links to completed tasks and comparisons of compatible baseline/follow-up entries. |
| History | A private timeline of project creation, assessments and observations; this is not a complete edit audit log. |
| Community sharing | Preview and consent before publication, unpublish, visitor reports and manual operator moderation. |
| Accessibility and data use | Standard/low-data preferences, keyboard improvements, responsive styles, dark/light mode and a print layout; full device validation remains pending. |

Start through **My dashboard → Create a draft**, or adapt an example from Discover. Assessments, checklists and observations stay private; publishing a story requires a separate confirmation.

## Evidence and limitations

External examples are attributed summaries, not AdaptTrail pilot results. Fictional demonstrations are labelled and must never count as impact. Published community stories are self-reported; featuring a story does not verify its claims.

Guidance uses transparent preliminary rules, not AI predictions or independently validated agricultural recommendations. Only exact crop names maize, corn and grain maize enable the limited crop-specific prompts. Seek relevant local expertise before applying an approach.

Weather is supporting context. Forecasts are model values, not measurements at a farm. Notices update on request and send no SMS, email or push alerts. Failed or outdated weather checks are identified; no drought diagnosis, yield forecast or crop-damage threshold is claimed.

Measurement comparisons require matching metrics/units and confirmation of comparable methods, scope and periods. Missing values are not zero, and differences do not establish that an action caused a change. No verified farmer impact, partnership or UN endorsement is claimed.

Low-data mode reduces optional assets but still requires a connection. Offline saving, translations, USSD/SMS access, automatic alerts, structured evidence review, team workspaces, advanced condition filters and cost/currency tracking remain future work. Password recovery and account deletion are also not yet available.

## Relationship to the Global Goals

The intended focus supports water conservation and climate adaptation, particularly SDG 6 (Clean Water and Sanitation) and SDG 13 (Climate Action). Shared learning may also support SDG 17 (Partnerships for the Goals). This is an independent initiative; alignment does not imply UN affiliation or endorsement.

Early progress should be measured by whether people can complete the journey, understand the guidance and record useful observations. Environmental impact claims require real measurements and stated limitations.

## Technology and budget

Python and Flask serve the application, with optional JavaScript enhancements. SQLite stores local data; hosted records use PostgreSQL through Supabase, with Flask-managed accounts. Render hosts the application and GitHub holds its development history.

The project aims to stay within free service allowances without paid AI dependencies. Limits and pricing must be checked before changing service usage; ongoing free capacity is not guaranteed.

## Next milestones

1. Finish stage 5's mobile, accessibility, slow-connection and print verification; fix and record any issues.
2. Begin stage 6 only when authorised: a small, consenting farmer pilot with local agricultural review and feedback.
3. Use pilot findings to prioritise further development. Planned outcomes must not be presented as achieved results.

## Running the project

Requires Python 3.10 or newer. Node.js is also needed for the JavaScript test command below. From the repository directory:

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

### Project files

| Path | Purpose |
| --- | --- |
| `app.py` | Routes, accounts, ownership checks and form handling. |
| `storage.py` | SQLite/PostgreSQL connections and local schema setup. |
| `assessment.py`, `guidance.py` | Preliminary assessment rules and explained planning prompts. |
| `weather.py`, `weather_notices.py` | Optional weather retrieval, saved context and on-demand notices. |
| `documented_projects.py` | Attributed external starter summaries. |
| `templates/`, `static/` | Server-rendered pages, styles and optional JavaScript. |
| `tests/`, `scripts/` | Automated checks and optional browser verification. |
| `sql/` | Hosted schema and feature migrations. |
| `hosted_verify.py`, `gunicorn.conf.py` | Hosted workflow verification and startup readiness checks. |
| `render.yaml`, `requirements.txt` | Deployment definition and pinned Python dependencies. |
| `docs/` | Feature notes, verification records and pilot preparation. |

The demonstration collection remains separate from user drafts. Create a draft through **My dashboard → Create a draft**. Drafts are stored in `instance/drafts.sqlite3` and persist after restarting. They can optionally reference a fictional demo as inspiration. Open a saved draft and choose **Edit draft** to update it, or **Delete draft** to review a confirmation page. Deletion requires an explicit confirmation and cannot be undone. Progress observations and explicit publication are implemented; private notes are not automatically published.

For local development, create an account with a username and a password of 8–128 characters, then sign in. Each account can access only its own drafts. Passwords are hashed and state-changing forms require CSRF tokens. Use the loopback development server locally. Production configuration enables secure cookies and basic authentication rate limiting and requires production secrets and a PostgreSQL connection. Password recovery is not implemented. Weather is optional; core recordkeeping works without a weather request.

The `instance/` directory and its session key are excluded from Git. To back up local drafts, stop the app and copy `instance/drafts.sqlite3` to a safe private location.

Run the Python workflow checks and JavaScript comparison tests:

```bash
python -m unittest discover -s tests -v
node --test tests/test_progress_comparison.cjs
```

Optional browser checks require Playwright, an installed Chromium browser and a running local app. See [stage 5 testing instructions](docs/STAGE_5.md) before running them. A browser test file being present does not mean its checks have passed.

## Licence

A code licence has not yet been selected. Contributor consent and reuse terms for community submissions must be addressed separately from the software licence.


## Existing drafts from before accounts

The database migration preserves older drafts with no owner. They are hidden from every account and are never automatically assigned to the first person who registers. After creating your account, the owner of the local installation can stop the server and explicitly assign all unowned drafts:

```bash
flask --app app assign-legacy-drafts YOUR_USERNAME
```

Use this only for drafts you own. It leaves already assigned drafts unchanged. Back up the SQLite file before migration or reassignment.


## Hosted deployment preparation

`render.yaml` defines a Free Render web service and an external PostgreSQL database connection. There is no Render database trial in this configuration. Hosted database workflows were verified during the stage 5 release on 21 October 2026. See [the verification record](docs/STAGE_5.md) for the tested release and remaining checks.

1. Create a dedicated Supabase Free project for AdaptTrail.
2. Apply `sql/hosted-schema.sql` to that project's SQL editor. Tables are stored in `adapttrail_private`, outside the exposed Data API. Do not expose this schema. The backend uses the dedicated application role; Flask enforces draft ownership. Follow the subsequent role, RLS, and feature migrations in `sql/` as well; this initial schema alone does not install every current feature. These accounts use Flask authentication, not Supabase Auth.
3. In Supabase's **Connect** dialog, copy the **Session pooler** connection string and insert the database password, percent-encoding reserved characters. Set this privately as `DATABASE_URL` in Render. Never commit it or paste it into public messages.
4. Render's Blueprint generates `SECRET_KEY` and sets `APP_ENV=production`. Missing production settings stop startup instead of falling back to disposable SQLite storage.
5. Deploy and verify registration, ownership isolation, restart persistence, and `/health` against the real database before inviting users.

Local accounts and drafts are not automatically copied to the hosted database. Back them up before any future import. A free provider URL can be used initially; no custom domain is required.

Production enables secure cookies, response security headers, and a basic sign-in/registration rate limit. The initial service uses one Gunicorn worker. Rate-limit counters are process-local and reset on restart; shared counters and trusted proxy-aware client addressing are future improvements. Password recovery and account deletion are still pending.

For exports, use Supabase's database backup/export tooling; keep exported account hashes and draft data private. After hosted schema or application changes, verify affected PostgreSQL workflows again. Local SQLite tests do not substitute for that check.

## Documentation

- [Feature reference](docs/FEATURES.md): detailed workflows, privacy boundaries, weather behavior and feature migrations.
- [Stage 5 verification](docs/STAGE_5.md): completed checks, test commands and remaining sign-off requirements.
- [Guidance rules](docs/GUIDANCE_RULES.md): rule map, sources and agricultural review requirements.
- [Weather notices](docs/WEATHER_NOTICES.md): refresh behavior, privacy, failure handling and limitations.
- [Pilot guide](docs/PILOT.md): preparation and feedback prompts; no completed pilot is implied.
- [Stage 1 review](docs/PLATFORM_REVIEW.md): historical review of the platform.

### Latest recorded verification

On 21 October 2026, **71 Python tests and 6 JavaScript tests passed**. Hosted verification exercised production database workflows, low-data preferences, ownership and temporary-record cleanup. Live desktop checks covered display preferences, omitted assets, keyboard skip focus and theme switching.

**Stage 5 is not fully signed off.** Mobile viewport and real-device testing, screen-reader checks, slow-connection verification and print-output inspection remain pending. Stage 6 has not started.
