# HammDroid Job Agent

HammDroid is a local job-search automation project that has progressed through two stages:

1. a **Python CLI prototype** for constructing targeted job searches and storing reviewed results in CSV
2. a **Hermes Agent + Google Sheets integration** for moving that structured state into an API-backed workflow

The repository is intentionally scoped to what has actually been built, configured, or tested. It does not present autonomous job discovery or application submission as finished functionality.

## What is actually implemented

### Local Python search prototype

[`prototype/job_finder_modes_local.py`](prototype/job_finder_modes_local.py) is a working local prototype that:

- defines job-search lanes as Boolean query fragments
- separates strict ATS searches from broader career-site searches
- includes low-years / education-substitution search phrases
- URL-encodes generated queries with `urllib.parse.quote_plus`
- opens the resulting search in the default browser
- stores manually reviewed jobs in a structured CSV with `csv.writer`
- initializes a repeatable record schema when the CSV does not exist

The core flow is:

```text
company
  + role lane
  + experience terms
  + location terms
  + site filter
        ↓
build_query()
        ↓
quote_plus()
        ↓
Google search URL
        ↓
manual review
        ↓
structured CSV row
```

The prototype uses only the Python standard library. Run it from the repository root with:

```bash
python prototype/job_finder_modes_local.py
```

It creates `job_finds.csv` in the current working directory. That local output file is ignored by Git so personal job-search state is not mixed with the source repository.

This prototype does **not** scrape search results or apply automatically.

### Google Sheets state integration

The current state-layer work uses Hermes Agent's Google Workspace tooling with Google OAuth and the Sheets API.

The tested path is:

```text
Hermes workflow
      ↓
Google Workspace skill/helper
      ↓
OAuth 2.0 token
      ↓
Google Sheets API
      ↓
structured spreadsheet state
```

The integration work includes:

- Google Desktop OAuth client setup
- credential/token path troubleshooting
- reducing broad Workspace permissions toward Sheets + read-only Drive access
- diagnosing OAuth `403 access_denied`
- diagnosing `403 SERVICE_DISABLED` for `sheets.googleapis.com`
- diagnosing a malformed HTTP 400 write request
- spreadsheet **create → write → read** round-trip validation

`append` has not been separately validated.

See [Google Sheets Integration](docs/google-sheets-integration.md) for the technical failure trail and [Technical Architecture](docs/architecture.md) for component boundaries.

## Why the project changed from CSV to Sheets

The Python prototype used this local schema:

```text
role
company
lane
site_found
years_expected
posted_date
date_found
url
status
notes
```

CSV was enough to prove the workflow, but an agent needs persistent state that can be read and updated independently of the browser session.

That led to this design change:

```text
local CSV
   ↓
works for a single local script
   ↓
need shared/readable agent state
   ↓
Google Sheets API
```

Sheets is being used as a lightweight structured state store, not as a replacement for a production database.

## Technical areas demonstrated

| Area | Hands-on work |
|---|---|
| **Python** | functions, dictionaries/configuration, input validation, `Path`, CSV I/O, URL encoding, browser invocation |
| **Search construction** | Boolean query composition, role lanes, ATS domain filtering, location/experience filters |
| **State design** | explicit job-record schema, CSV persistence, migration concept from local file state to Sheets |
| **OAuth 2.0** | Desktop client flow, test-user access, token storage, scope reduction, callback/path troubleshooting |
| **Google Sheets API** | API activation, create/write/read validation, malformed request debugging |
| **Integration troubleshooting** | separating credential discovery, OAuth, scope, API-service, request-format, and application-state failures |
| **Security boundaries** | secrets excluded from Git, reduced OAuth scope target, human stops for consequential actions |

## Implementation boundary

This repo does **not** claim that I wrote Hermes Agent, an inference engine, or Google's OAuth/Sheets client libraries.

My work is the configuration and integration around those components plus the Python job-search prototype.

```text
external component             work represented here
────────────────────────────────────────────────────────
Hermes Agent runtime        → workflow/tool configuration
Google OAuth               → client setup, scopes, token-flow troubleshooting
Google Sheets API          → integration and request troubleshooting
Python standard library    → local job-search prototype
```

The retained project evidence does not currently include enough configuration to make a precise public claim about the active local model/provider, so the repo does not use the model choice as a technical accomplishment.

## Failure-driven troubleshooting

The most useful part of the integration work was learning not to collapse every Google failure into "OAuth is broken."

```text
403 access_denied
→ OAuth consent / test-user layer

credential file not found by helper
→ runtime path-resolution layer

403 SERVICE_DISABLED
→ Google Cloud API-enable layer

HTTP 400 malformed write
→ Sheets request-format layer
```

Each response changed the next troubleshooting question rather than triggering a full reconfiguration.

## Current project status

### Working / validated

- Python query-building prototype
- browser launch of encoded search queries
- structured CSV output
- Hermes CLI/runtime availability
- Google Desktop OAuth setup
- Sheets API enablement
- spreadsheet create/write/read round trip
- credential exclusions in `.gitignore`

### Not yet claimed as working

- automated job-result parsing
- automated deduplication
- fit classification
- production job tracker
- append validation
- browser-driven application workflow
- CAPTCHA/MFA handling beyond stopping for the user
- application submission

## Safety boundary

Consequential application actions remain human-controlled. The intended workflow stops for:

- CAPTCHA
- MFA/passkeys
- legal attestations
- assessments
- unknown factual questions
- final application submission

The system must not invent employers, dates, experience, clearances, certifications, skills, or application answers. Coursework, labs, homelabs, and portfolio work are not represented as professional employment.

## Repository map

```text
README.md
prototype/
  job_finder_modes_local.py

docs/
  architecture.md
  google-sheets-integration.md
```

No OAuth client secrets, tokens, authorization codes, browser sessions, or other credentials are stored in this repository.
