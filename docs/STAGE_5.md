# Stage 5 — mobile usability, accessibility and low-data access

## Repository review
Starting main commit: 88f8c37f7f03342aedbac480ef96f8b397d38281.
Reviewed the repository tree, shared templates/styles/scripts, assessment, checklist,
weather and progress screens, request hooks, CSRF handling and existing test conventions.
No AGENTS.md was present in the repository tree.

Existing strengths: responsive breakpoints, semantic labels, reduced-motion support,
server-rendered forms, an Escape-aware menu and on-demand weather.
Gaps addressed: inherited full-width checkbox styling, narrow-screen wrapping,
small controls, keyboard access to overflow tables, error focus, unassociated
character counts, and no user-selectable low-data mode.

## Changes
- Improve layout reflow, long-content wrapping, 44px button/select/summary targets,
  16px text inputs and checkbox/radio controls with large clickable labels.
- Make the skip-link destination focusable. Focus server-rendered errors when
  JavaScript is available. Name and focus weather-table scroll regions.
- Associate character counters with their textareas without removing existing help.
- Add /accessibility with a CSRF-protected server-rendered mode form.
- Store an explicit standard/low-data preference in a separate, HttpOnly, SameSite
  cookie for up to one year (Secure in production); it survives login/logout.
  An explicit choice overrides the browser Save-Data hint.
- Low-data HTML omits app.js and the homepage illustration, reducing uncached
  asset requests and bytes. It keeps navigation and all assessment questions
  visible. Other small page-specific scripts and theme/feedback scripts remain.
  Savings are modest; no transfer-size benchmark has been run.
- Mark personalized HTML no-store and vary it by Cookie and Save-Data.
  Static assets retain their existing caching behavior.
- Add a print layout for browser Print/Save as PDF. Expand any details sections
  you need before printing; browser support differs. This is not offline app use.

## Verification status
Performed in this session:
- Read and reviewed source through GitHub.
- Parsed changed application JavaScript and the new browser-check script.
- Exercised accessibility error-focus and no-error paths with a minimal DOM stub.

Not run: Python tests, a running Flask instance, browser checks, screenshots,
real-device checks, assistive-technology checks or production deployment verification.
The execution environment was unavailable. Do not describe these as passing.

Added tests:
- tests/test_accessibility.py: mode switching, asset omission, browser hint
  precedence, CSRF/invalid-input rejection, cookie/session independence and
  personalized HTML cache headers.
- scripts/verify-stage5.cjs: public-page reflow at 320/390/768/1440px, skip focus,
  menu/Escape focus, theme toggle, no-JavaScript preferences and omitted assets.

Run with project dependencies installed and a local test database:
```sh
python -m unittest discover -s tests -q
node --test tests/test_progress_comparison.cjs
GUI_TEST_URL=http://127.0.0.1:5055 node scripts/verify-stage5.cjs
```
The browser script additionally requires Playwright and an installed Chromium
browser; GUI_BROWSER_PATH may point to an existing browser.

## Remaining manual checks before calling the stage validated
- At 320px and with 200%/400% zoom, inspect authenticated assessment, checklist,
  weather and progress screens using long project names and saved content.
- Keyboard-test table horizontal scrolling, error focus and described counters.
- Test screen-reader labels and errors, contrast in both themes and reduced motion.
- Save an assessment without weather; complete a task and add an observation
  in standard mode, low-data mode and with JavaScript disabled.
- Use a slow connection and check the Network panel: no app.js or landscape.svg
  request in low-data mode, weather requests only when explicitly requested.
- Print an assessment containing a forecast; verify source, retrieval time,
  limitations, table columns and expanded details remain readable.

## Boundary
Stage 5 implementation is committed; runtime and device validation remain pending.
No Stage 6 work, SMS/USSD integration, offline form queue, notification delivery,
database migration or measured-impact claims are included.
