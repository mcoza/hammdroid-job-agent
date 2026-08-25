# Python Prototype Evolution

The Python portion of HammDroid exists in two retained stages. Keeping both versions makes the progression inspectable instead of describing it only in prose.

## Version 1: one search strategy + CSV state

[`prototype/job_finder_csv_local_v1.py`](../prototype/job_finder_csv_local_v1.py) used one combined site filter and a fixed workflow:

```text
company
  + selected role lane
  + experience terms
  + location terms
  + site filters
        ↓
quote_plus(query)
        ↓
webbrowser.open_new_tab(url)
```

A manually reviewed result could then be stored with:

```python
with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
    csv.writer(file).writerow(row)
```

The CSV schema was explicit:

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

This proved the simplest end-to-end state transition:

```text
search configuration → browser query → human review → structured local record
```

## Version 2: separate search modes

[`prototype/job_finder_modes_local.py`](../prototype/job_finder_modes_local.py) kept the same basic state model but separated search behavior into three modes:

```text
1. Strict ATS-only
2. Broad career sites
3. Exact low-years phrase search
```

The site filters became separate configuration values instead of one `SITES` constant:

```python
STRICT_ATS_SITES = (...)
BROAD_CAREER_SITES = (...)
```

and query assembly moved into a dedicated function:

```python
def build_query(company, lane_terms, mode_name, sites):
    ...
```

That was a small architectural improvement with a concrete purpose: query logic could change by mode without duplicating the browser-launch or CSV-recording workflow.

## What this code does not do

Neither retained version:

- scrapes Google result pages
- parses ATS pages
- scores job fit automatically
- deduplicates jobs automatically
- submits applications

The code is intentionally a human-in-the-loop search and recording prototype. The later agent/Sheets work was an attempt to move the persistent state and orchestration beyond this local CLI without pretending the search prototype already performed those missing steps.
