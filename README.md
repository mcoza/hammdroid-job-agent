# HammDroid Job Agent

HammDroid is a small job-search workflow project. It started as a Python helper for building targeted searches and recording reviewed jobs, then expanded into a Hermes Agent + Google Sheets integration so the same job state could be shared outside a local CSV file.

## What is here

```text
job_finder.py
examples/
  job_finds_poc.csv
  search_test_results.csv
docs/
  google-sheets-integration.md
```

The repository intentionally stays close to the work that was actually built and tested. It is not presented as a finished autonomous application system.

## Python search helper

Run:

```bash
python job_finder.py
```

The script lets a user choose a job-search lane and one of three search modes:

- strict ATS domains
- broader company career sites
- exact low-experience qualification phrases

It combines the selected terms with location and experience filters, URL-encodes the query with `urllib.parse.quote_plus`, opens it in the browser, and can save a manually reviewed result to `job_finds.csv`.

The stored fields are:

```text
role, company, lane, site_found, years_expected,
posted_date, date_found, url, status, notes
```

The script does **not** scrape result pages or submit applications.

## Search strategy testing

The search modes were added after testing different query strategies against real career sites. The main finding was that strict ATS-only searches worked, but were too narrow by themselves for some defense-contractor searches.

The better pattern was:

```text
company career page / ATS domain
+ role terms
+ exact low-years qualification phrases
+ location terms
```

The retained test results also show why manual review still matters: a search can match useful qualification language while the title, location, or eligibility requirements still make the posting a poor fit.

See [`examples/search_test_results.csv`](examples/search_test_results.csv) for the original test results and [`examples/job_finds_poc.csv`](examples/job_finds_poc.csv) for the initial spreadsheet-ready record shape.

## Hermes + Google Sheets work

The next step was moving the same basic state model from a local CSV toward Google Sheets, with Hermes Agent used as the external agent runtime.

The integration work included:

- Google Desktop OAuth setup
- reducing unnecessary Google Workspace permissions
- tracing a credential-path problem to the Hermes home directory used by the helper
- resolving OAuth/test-user access issues
- enabling the Google Sheets API after a `SERVICE_DISABLED` response
- correcting a malformed Sheets write request
- validating a spreadsheet create → write → read round trip

Append behavior was not separately validated.

The troubleshooting sequence is summarized in [`docs/google-sheets-integration.md`](docs/google-sheets-integration.md).

## Current boundary

**Built/tested here:** Python query generation, browser launch, CSV state, search-method testing, OAuth/Sheets setup and troubleshooting.

**Not implemented:** automatic result extraction, automatic deduplication, fit scoring, or application submission.

OAuth secrets, tokens, browser sessions, and local Hermes state are excluded from Git.
