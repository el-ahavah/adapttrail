# AdaptTrail

**A Green Code, Green Planet initiative.**

**A shared memory of climate action: discover an experience, assess its fit, adapt it locally, measure what happens, and share the lessons.**

## Project status

The first Flask prototype is implemented: Home, Discover, action filtering, fictional project detail pages, and local project drafts saved in SQLite. It runs locally and has not been deployed. Accounts, hosted storage, assessments, progress observations, and publication are planned. No partnerships, UN affiliation, verified impact, or worldwide originality are claimed.

## The idea

AdaptTrail will help communities find climate adaptation experiences from other places, understand the evidence behind them, and document their own adaptations. Green Code, Green Planet is the broader initiative behind the platform.

The platform will begin with water conservation. Users will explore what others tried, the conditions they faced, the resources they needed, and the results they reported—including unsuccessful attempts. The broader vision includes agriculture, heat resilience, flood preparedness, and ecosystem restoration. Each additional area will require its own relevant data and reviewed guidance.

The intended point of difference is connecting related attempts into a traceable history: where an idea began, how another community changed it, and what happened under different conditions. Matching will consider relevant conditions rather than country alone. This direction still requires comparison with existing platforms and conversations with potential users.

## Optional suitability guidance

The core journey is **Discover → Assess → Adapt → Track → Share**.

Users can browse climate solutions without providing a location or completing an assessment. When they want help deciding whether an approach fits, they can choose **“Help me assess this approach.”** Location and weather are supporting factors alongside their goals, soil, crops, resources, and other relevant conditions.

The assessment considers only factors relevant to the selected action:

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

The first assessment will use a small set of documented, reviewed rules for selected water-conservation approaches. Weather integration is a later enhancement unless a suitable source, reuse terms, coverage, and free allowance are confirmed. If weather data is unavailable, browsing and project tracking still work; the assessment identifies the gap.

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

Begin with a small curated collection of real water-conservation case studies whose reuse terms permit inclusion. Keep attribution, source links, publication dates, and limitations. No real case studies have been collected yet.

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

- Weather-data integration and richer suitability assessments.
- Map-based discovery as an optional browsing aid.
- Team workspaces and structured practitioner review.
- Multilingual content and translation with access to the original text.
- AI summaries and explained suggestions linked to supporting records.
- Low-connectivity draft capture and later synchronisation.
- Expansion to other adaptation challenges after validating water conservation.

AI must not invent evidence, mark claims as verified, or promise outcomes. Paid AI services are not required for the MVP.

## Technology and budget

Python and Flask are the proposed application stack. GitHub will hold the code and development history.

Hosting and database choices are **not yet finalised**. Options discussed include Render Free for the application, and Supabase Free or Neon Free for the database. Supabase is a candidate for accounts and file storage as well. Provider choices remain subject to checking current terms and application requirements. The project owner's requirement is no recurring hosting or database charges while operating within free-plan allowances. Expiring database trials should be avoided.

Free plans have capacity and availability limits, and providers can change their terms. A custom domain is optional and generally has a recurring registration renewal. A free provider address can be used initially. Public deployment should wait until persistent storage, access controls, configuration, and backup/export procedures are checked.

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

The demonstration collection remains separate from user drafts. Create a draft through **My drafts → Create a draft**. Drafts are stored in `instance/drafts.sqlite3` and persist after restarting. They can optionally reference a fictional demo as inspiration. Editing, deletion, progress observations, and public publication are not implemented yet.

This is a local, single-user prototype with no accounts. Anyone who can access the running app can read the drafts. Run on the default loopback address only; do not expose it publicly. Shared deployment requires authentication and per-user ownership checks. SQLite here is a learning step, not the selected hosted database. No weather API or paid services are required.

The `instance/` directory and its session key are excluded from Git. To back up local drafts, stop the app and copy `instance/drafts.sqlite3` to a safe private location.

Run the persistence and form checks:

```bash
python -m unittest discover -s tests -v
```

## Licence

A code licence has not yet been selected. Contributor consent and reuse terms for community submissions must be addressed separately from the software licence.
