# HammDroid Job Agent

HammDroid is my attempt to make job searching less repetitive without jumping straight to a giant autonomous application system.

I built it in layers because I wanted each piece to answer a real problem before I added the next one:

```text
manual search ideas
→ local Python search helper
→ tested search modes
→ structured CSV state
→ Hermes Agent integration
→ Google Sheets API state
→ future local-first automation
```

The point of the repo is not "AI applies to jobs." It is to show what I tried, what I learned from the results, why the design changed, and what is actually working now.

## The problem I was trying to solve

Job discovery was repetitive and inconsistent:

- relevant roles are split across ATS platforms and employer career sites
- early-career cybersecurity roles do not use one consistent title
- qualification language can be more useful than title wording
- broad searches still return senior, wrong-location, or otherwise weak matches
- manually rebuilding the same searches and tracking the results wastes time

So my first question was smaller than "how do I automate applications?"

```text
Can I make discovery and tracking repeatable
while keeping the final judgment under human control?
```

## 1. Prove the search logic locally

The current helper is [`job_finder.py`](job_finder.py).

It lets me choose a job-search lane and one of three search modes:

```text
1. Strict ATS-only
2. Broad career sites
3. Exact low-years phrase search
```

The script combines:

```text
company
+ role terms
+ experience terms
+ location terms
+ site filter
```

then URL-encodes the query with `urllib.parse.quote_plus`, opens it in the browser, and lets me save a reviewed result to `job_finds.csv`.

The stored fields are:

```text
role, company, lane, site_found, years_expected,
posted_date, date_found, url, status, notes
```

The original simpler proof of concept is retained in [`prototype/job_finder_poc.py`](prototype/job_finder_poc.py), and the later mode-based version is retained in [`prototype/job_finder_modes_local.py`](prototype/job_finder_modes_local.py).

Run the current helper with:

```bash
python job_finder.py
```

The script does **not** scrape result pages or submit applications.

## 2. Change the search strategy when the results say I should

I started with common ATS domains because they gave me a narrower target than general web search.

Testing showed that ATS-only search worked, but it was too narrow for some employers. Company career pages and exact low-experience qualification phrases sometimes produced better results.

That is why the script gained multiple modes instead of one increasingly huge query.

The retained test data shows examples where:

```text
strict ATS search
→ found valid Workday roles

company career-page search
→ found additional low-years roles

exact qualification phrase
→ surfaced associate/pathways-style roles
```

It also showed why search matches still need review. A result could have good qualification language but still have a `Principal` title, the wrong location, or a senior experience requirement.

See [Search Strategy Experiments](docs/search-experiments.md) and [`examples/search_test_results.csv`](examples/search_test_results.csv).

## 3. Keep human review before turning a result into state

I deliberately did **not** make the first version decide "this is a good job, apply now."

My early flow is:

```text
search
→ inspect the actual posting/result
→ decide whether it is useful
→ save the structured record
```

That choice came from the test results. Search engines are good at retrieving candidate pages; that is not the same as understanding whether the posting is actually appropriate.

The example CSVs show the record shape and the candidate/skip-style review that informed the next version.

## 4. Start with CSV instead of overbuilding the state layer

I used CSV first because I needed to prove the fields and workflow, not build infrastructure.

At that stage the useful question was:

```text
Can I reliably capture the information I care about?
```

The answer was yes, and the schema was simple and tabular.

That meant I had a usable state model before deciding where that state should live long term.

## 5. Move toward Google Sheets instead of adding a database

When I started connecting the workflow to Hermes Agent, I wanted state that was:

- persistent
- structured
- API-accessible
- easy for the agent to read/write
- easy for me to inspect or correct directly

Google Sheets fit that stage of the project better than a database.

My reasoning was:

```text
CSV
→ proves the schema locally
→ tied to one local file/workflow

Google Sheets
→ keeps the same table model
→ adds API access
→ remains directly human-readable/editable
```

I am not treating Sheets as a production database. If I eventually need stronger concurrency, relational data, larger history, or transactional guarantees, that would be evidence for adding a database. I do not need that complexity yet.

## 6. Use an API for structured state instead of clicking spreadsheet cells

The current integration path is:

```text
Human
  ↓
Hermes Agent
  ↓
Google Workspace helper
  ↓
OAuth 2.0 token
  ↓
Google Sheets API
  ↓
structured spreadsheet state
```

The work included:

- Google Desktop OAuth setup
- tracing a credential-path mismatch to the Hermes home used by the helper
- OAuth/test-user troubleshooting
- reducing unrelated Workspace permissions
- enabling `sheets.googleapis.com` after `SERVICE_DISABLED`
- correcting a malformed Sheets write request
- validating **create → write → read**

Append behavior has not been separately validated.

See [Google Sheets Integration](docs/google-sheets-integration.md).

## 7. Keep routine work local when practical

A design goal for HammDroid is to avoid making every repetitive search, classification, or orchestration step depend on paid cloud-model tokens.

The direction I am aiming for is:

```text
routine repetitive work
→ local agent/model where practical

important or uncertain decision
→ optional stronger cloud-model review/check
```

That is a design direction, not a claim that the full local/cloud review pipeline is finished today.

I want the local system to handle the routine work when it can, while still leaving room for a stronger external model to review ambiguous decisions occasionally rather than paying for every small step.

## 8. Keep consequential application actions human-controlled

There are points where I do not want the agent guessing or silently acting.

The intended workflow stops for:

- CAPTCHA
- MFA/passkeys
- legal attestations
- assessments
- factual questions the system cannot verify
- final application submission

The system also must not invent employers, dates, experience, clearances, certifications, skills, or application answers.

That is both a safety boundary and a data-integrity boundary.

## What is working now

**Built/tested:**

- Python query construction
- selectable search modes
- browser launch of encoded searches
- structured CSV output
- manual result review
- retained search-strategy test data
- Hermes CLI/runtime availability
- Google Desktop OAuth setup
- credential-path troubleshooting
- Sheets API enablement
- spreadsheet create/write/read validation
- secrets/tokens excluded from Git

**Not claimed as finished:**

- automatic result-page extraction
- automatic deduplication
- fit classification
- production job tracker
- append validation
- complete local/cloud reviewer pipeline
- automated application completion
- application submission

## Repository map

```text
job_finder.py                 current local helper

prototype/
  job_finder_poc.py           original simpler POC
  job_finder_modes_local.py   mode-based iteration

examples/
  job_finds_poc.csv           initial record shape
  search_test_results.csv     search-method test results

docs/
  design-decisions.md         why I made the architecture choices
  search-experiments.md       why the search modes changed
  google-sheets-integration.md OAuth / Sheets troubleshooting trail
```

For the reasoning behind the project, start with [Design Decisions and Why I Made Them](docs/design-decisions.md).

No OAuth client secrets, access/refresh tokens, authorization codes, browser sessions, generated local job-tracking files, or local Hermes state are stored in this repository.
