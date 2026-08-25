# Technical Architecture

HammDroid is currently an **integration project**, not a custom agent framework. The agent runtime is provided by Hermes Agent. My work has been configuring the workflow around it, testing Google OAuth/Sheets access, defining job-search state, and iterating on a local Python search prototype.

That distinction matters because this repository should show what I actually built or configured instead of implying that I wrote Hermes, an LLM runtime, or the Google client libraries.

## Current implementation boundary

```text
                    code/config I control
                    ─────────────────────────────────────

Human input
    ↓
Hermes Agent configuration / workflow rules
    ↓
Hermes Google Workspace skill configuration
    ↓
OAuth credential + token handling
    ↓
Google Sheets API operations
    ↓
structured job-search state

                    ─────────────────────────────────────
                    external/runtime components
```

Hermes supplies the agent runtime and tool execution layer. Google supplies OAuth and the Sheets API. HammDroid's current technical work is the **configuration, integration, troubleshooting, state design, and workflow constraints between those systems**.

## Earlier local prototype

Before the agent/Sheets integration, I built a small Python CLI prototype that performed two concrete tasks:

```text
company + search lane + search mode
              ↓
build_query()
              ↓
Google search query
              ↓
quote_plus()
              ↓
webbrowser.open_new_tab()
```

and:

```text
manually reviewed job
        ↓
collect structured fields
        ↓
csv.writer.writerow()
        ↓
job_finds.csv
```

The source is retained in [`prototype/job_finder_modes_local.py`](../prototype/job_finder_modes_local.py).

The prototype is intentionally simple. It does **not** scrape job sites or submit applications. It builds targeted searches and records manually reviewed findings in a structured local CSV.

## Prototype data model

The CSV schema is explicit in code:

```python
HEADERS = [
    "role",
    "company",
    "lane",
    "site_found",
    "years_expected",
    "posted_date",
    "date_found",
    "url",
    "status",
    "notes",
]
```

This is the state model that later motivated moving from a local CSV to Google Sheets: the workflow needs persistent structured records that can be read and updated by an agent while remaining easy for a human to inspect.

## Search-query construction

The prototype separates search intent into configuration instead of hard-coding one query.

### Role lanes

`LANES` maps a user selection to a label and a Boolean search expression. Examples include GRC/audit, defense/RMF, SOC/security analysis, IT support, and vendor/privacy risk.

### Experience filter

`EXPERIENCE` contains low-years and education-substitution phrases used to bias the search toward roles that are plausible for an early-career applicant.

### Site targeting

Two search modes are implemented:

```text
Strict ATS-only
→ Workday / Greenhouse / Lever / iCIMS / Taleo / SmartRecruiters

Broad career sites
→ ATS domains plus selected employer career domains / broader career patterns
```

A third mode searches exact low-years education phrases.

### Query encoding

The query is converted into a browser-safe URL using:

```python
url = "https://www.google.com/search?q=" + quote_plus(query)
```

`quote_plus()` URL-encodes spaces and reserved characters so the constructed Boolean query can be passed in the Google search URL.

## Current Sheets state path

The current integration replaces the CSV as the intended state layer:

```text
Hermes workflow
    ↓
Google Workspace skill
    ↓
OAuth 2.0 token
    ↓
Google Sheets API
    ↓
spreadsheet rows/cells
```

The tested integration is documented in [`google-sheets-integration.md`](google-sheets-integration.md).

## Credential flow

The Hermes Google Workspace helper resolves credential/token files from the Hermes home directory. The setup work used these logical files:

```text
google_client_secret.json  → OAuth Desktop client configuration
google_oauth_pending.json  → temporary authorization-flow state
google_token.json          → stored OAuth token/refresh information
```

These files are deliberately excluded by `.gitignore`.

The flow is:

```text
Desktop OAuth client JSON
        ↓
OAuth authorization request
        ↓
user consent / callback
        ↓
token exchange
        ↓
stored token
        ↓
authenticated Sheets API request
```

## What has been validated

Supported by the retained project work:

```text
Hermes CLI installed / available                     validated
Google Desktop OAuth client used                     validated
OAuth test-user issue diagnosed                      validated
Sheets API SERVICE_DISABLED failure diagnosed        validated
Sheets API enabled                                   validated
spreadsheet create → write → read round trip         documented as validated
append operation                                     not separately validated
full job-discovery agent                             not implemented
job-site scraping                                    not implemented
application submission                               not implemented
```

## What is intentionally not claimed

This repository does not claim that I implemented:

- Hermes Agent itself
- an LLM inference engine
- Google's OAuth libraries
- a production web scraper
- autonomous job applications
- CAPTCHA/MFA bypass
- a production-grade database

The technical value of the project is in the integration work: moving from a local Python/CSV proof of concept toward an agent workflow with API-backed structured state, while debugging authentication, API-service, request-format, and permission boundaries.
