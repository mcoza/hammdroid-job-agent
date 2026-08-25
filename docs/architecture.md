# Technical Architecture

HammDroid currently has two concrete layers:

1. a Python CLI that builds searches and stores reviewed jobs locally
2. integration work that connects an external Hermes runtime to Google OAuth / Sheets tooling

The repository separates **code I wrote**, **configuration/integration I changed**, and **external components** so the architecture does not imply ownership of third-party systems.

## 1. Python execution path

The current source is [`prototype/job_finder_modes_local.py`](../prototype/job_finder_modes_local.py).

```text
main()
  ↓
read company from stdin
  ↓
choose_lane()
  ↓
choose_search_mode()
  ↓
build_query(company, lane_terms, mode_name, sites)
  ↓
quote_plus(query)
  ↓
webbrowser.open_new_tab(url)
```

A reviewed job follows a separate path:

```text
main()
  ↓
save_good_find(company)
  ↓
collect fields from stdin
  ↓
build row in HEADERS order
  ↓
open job_finds.csv in append mode
  ↓
csv.writer(file).writerow(row)
```

`setup_csv()` creates the file and writes the header row only when the CSV does not already exist.

## 2. Query configuration

Search behavior is configuration-driven rather than embedded in one long query string.

```text
LANES
  ├─ GRC / Audit / Compliance
  ├─ Defense / RMF / NIST
  ├─ SOC / Security Analyst
  ├─ IT Support / Security Adjacent
  └─ Privacy / Vendor Risk

EXPERIENCE
LOCATION
EXCLUDE
STRICT_ATS_SITES
BROAD_CAREER_SITES
```

`build_query()` combines those values differently depending on the chosen mode.

The earlier retained source used one `SITES` constant. The newer version split that into separate strict/broad modes and added a dedicated `build_query()` function. Both versions are retained so that change is inspectable. See [Python Prototype Evolution](prototype-evolution.md).

## 3. Local state schema

The state model is a ten-column record:

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

The prototype does not treat this as an ORM or database model. It is simply the ordered schema used to serialize manually reviewed jobs to CSV.

## 4. Agent / Sheets integration boundary

The later integration work used an external Hermes Agent runtime and its Google Workspace helper.

```text
HammDroid workflow/configuration
        ↓
Hermes Agent runtime
        ↓
Google Workspace helper
        ↓
OAuth credential/token handling
        ↓
Google API request
        ↓
spreadsheet state
```

### HammDroid-controlled work

- job-search workflow rules
- job-record schema
- Python prototype
- selection of required Google scopes
- placement/configuration of runtime credential paths
- troubleshooting of integration failures
- human-stop rules for consequential actions

### External implementation

- Hermes Agent CLI/runtime/tool execution
- Google OAuth authorization service
- Google Sheets API
- browser and search engine

## 5. Credential path behavior observed during setup

The retained setup transcript showed the Google Workspace helper building paths from a Hermes home location, including:

```python
CLIENT_SECRET_PATH = HERMES_HOME / "google_client_secret.json"
PENDING_AUTH_PATH = HERMES_HOME / "google_oauth_pending.json"
```

A concrete failure occurred when the Desktop OAuth JSON existed in one directory but the standalone setup helper resolved its credential path under `~/.hermes`.

```text
file exists
  +
helper reports no client secret
        ↓
inspect path construction
        ↓
compare actual file location with resolved CLIENT_SECRET_PATH
```

That troubleshooting trail is preserved in [`evidence/google-oauth-debugging.md`](../evidence/google-oauth-debugging.md).

## 6. Scope boundary

The broad Workspace helper scopes were not appropriate for a job tracker that primarily needed spreadsheet state.

The retained setup work targeted:

```python
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]
```

This was intended to remove Gmail, Calendar, Contacts, Docs, and full Drive permissions while retaining Sheets read/write access and read-only Drive visibility.

The repository is explicit that `drive.readonly` still grants read-only visibility beyond a single spreadsheet.

## 7. Runtime evidence

A local `hermes --help` capture is retained in sanitized form at [`evidence/hermes-runtime.md`](../evidence/hermes-runtime.md). It proves that the runtime/CLI was present during the project without treating Hermes itself as HammDroid code.

## 8. Evidence boundary

The source repository directly demonstrates:

```text
Python query generation      yes
URL encoding/browser launch  yes
CSV schema/write path        yes
Hermes CLI presence          retained runtime evidence
OAuth path investigation     retained setup evidence
scope reduction work         retained setup evidence
```

Later notes describe Sheets API error handling and a create/write/read round trip, but the raw API request/response artifact was not recovered with the retained chat export. The architecture therefore does not use that later result as proof of an implemented Sheets client.

## 9. Not implemented

The repository does not currently contain code for:

- job-site scraping
- automatic result extraction
- automatic deduplication
- fit scoring/classification
- a production database
- automated application submission
- CAPTCHA/MFA bypass

Those remain future workflow requirements rather than current architecture components.
