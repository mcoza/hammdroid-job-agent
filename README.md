# HammDroid Job Agent

HammDroid is a local job-search workflow project that started as a Python CLI and then moved toward an agent + Google Sheets integration.

The repository is organized around **inspectable implementation and troubleshooting evidence**. It does not claim autonomous job discovery or application submission as finished functionality.

## What is actually in the repository

```text
prototype/
  job_finder_csv_local_v1.py   original retained CLI prototype
  job_finder_modes_local.py    later prototype with selectable search modes

docs/
  prototype-evolution.md       code-level progression from v1 to v2
  architecture.md              component and data boundaries
  google-sheets-integration.md retained integration troubleshooting

evidence/
  hermes-runtime.md            sanitized local CLI evidence
  google-oauth-debugging.md    sanitized OAuth/path/scope investigation
```

No OAuth client secrets, tokens, authorization codes, browser sessions, or other credentials are stored here.

## 1. Python search prototype

The working Python prototype uses only the standard library.

The basic data path is:

```text
company
  + role lane
  + experience terms
  + location terms
  + search-mode site filter
        ↓
build_query()
        ↓
urllib.parse.quote_plus()
        ↓
webbrowser.open_new_tab()
        ↓
human reviews results
        ↓
csv.writer.writerow()
        ↓
job_finds.csv
```

The current version implements:

- five role/search lanes
- strict ATS, broad career-site, and exact low-years search modes
- Boolean query construction
- URL encoding with `quote_plus`
- browser launch
- input validation for lane/mode selection
- a ten-field job-record schema
- CSV initialization and append-style row writes

Run it from the repository root with:

```bash
python prototype/job_finder_modes_local.py
```

The earlier retained version is also included so the iteration can be inspected directly instead of inferred from documentation. See [Python Prototype Evolution](docs/prototype-evolution.md).

## 2. State model

Both Python versions use the same core record shape:

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

CSV was enough for the first local workflow, but it couples the state to one script and one filesystem. That motivated the next design question:

```text
local script state
      ↓
need state that an agent and a human can both inspect/update
      ↓
Google Sheets API integration
```

Sheets is being treated as a lightweight structured state layer, not as a production database.

## 3. External agent runtime actually observed

The local environment included a working Hermes Agent CLI. A retained `hermes --help` capture showed commands for configuration, skills, tools, projects, verification, logs, sessions, serving the backend, desktop mode, and one-shot invocation.

That evidence is preserved in [Hermes Runtime Evidence](evidence/hermes-runtime.md).

Hermes is an external runtime. HammDroid does **not** claim to implement Hermes, an inference engine, or its tool-calling framework.

## 4. Google OAuth integration: concrete troubleshooting

The strongest retained integration artifact is the setup/debugging trail rather than a finished wrapper library.

### Credential discovery

The Desktop OAuth client file existed and was valid, but the Google Workspace setup helper still reported that no client secret was stored.

The investigation moved from credential validity to path resolution:

```text
credential JSON exists
        ↓
helper still cannot find it
        ↓
inspect CLIENT_SECRET_PATH / HERMES_HOME resolution
        ↓
standalone helper resolves under ~/.hermes
        ↓
credential location and helper lookup path did not match
```

This is documented with sanitized paths in [Google OAuth / Hermes Integration Evidence](evidence/google-oauth-debugging.md).

### Scope reduction

The stock Workspace helper exposed broader permissions than the job-tracking workflow needed. The setup work narrowed the target toward:

```python
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]
```

That intentionally excludes Gmail, Calendar, Contacts, Docs, and full Drive access. `drive.readonly` is still general read-only Drive visibility, so it is not described here as single-file isolation.

### Redirect handling

The retained setup transcript also investigated a localhost redirect difference between the Desktop credential and the helper. The transcript does not retain a definitive token-exchange result, so this repository records that as an investigated issue rather than presenting a confirmed fix.

## 5. Evidence status

| Area | Repository evidence | Status |
|---|---|---|
| Python search/query construction | two retained `.py` versions | demonstrated |
| CSV state schema/write path | source code | demonstrated |
| Hermes runtime availability | sanitized CLI output | demonstrated |
| OAuth Desktop credential use | retained setup transcript, secret removed | demonstrated |
| Hermes credential-path debugging | retained setup transcript | demonstrated |
| Workspace scope reduction | retained setup transcript / sanitized target config | demonstrated as setup work |
| Sheets API create/write/read | described in later project notes, raw request/response not retained here | **not presented as reproduced evidence** |
| automated result parsing | no implementation | not implemented |
| fit classification / deduplication | no implementation | not implemented |
| application submission | intentionally human-controlled | not implemented |

## 6. Current component boundary

```text
HammDroid-controlled pieces
────────────────────────────────────────
Python query/state prototype
job-record schema
workflow constraints
OAuth/Sheets integration configuration
integration troubleshooting documentation

External pieces
────────────────────────────────────────
Hermes Agent runtime/tool layer
Google OAuth service
Google Sheets API
browser/search engine
```

The point of the project is not to relabel external tooling as custom code. The useful technical work is in the interfaces between these pieces: query construction, state design, runtime configuration, credential discovery, scope selection, and failure isolation.

## Safety boundary

Consequential application actions remain human-controlled. The intended workflow stops for CAPTCHA, MFA/passkeys, legal attestations, assessments, unknown factual questions, and final submission.

The system must not invent employers, dates, experience, clearances, certifications, skills, or application answers. Coursework, labs, homelabs, and portfolio work are not represented as professional employment.
