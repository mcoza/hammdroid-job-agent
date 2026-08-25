# Design Decisions and Why I Made Them

HammDroid started from a practical problem: job searching was repetitive, fragmented across ATS platforms and company career sites, and especially noisy for early-career cybersecurity roles.

I did not want to begin by building a large autonomous system and then hope it worked. My approach has been to prove each layer with the smallest useful version first, keep the parts I can inspect, and only add complexity when the earlier version shows why I need it.

## 1. Prove the search logic before adding an agent

My first question was not "how do I make an AI apply to jobs?"

It was:

```text
Can I create repeatable searches that find the kinds of roles I actually want?
```

That led to a local Python CLI that combines:

```text
company
+ role lane
+ experience phrases
+ location terms
+ site filters
```

into a search query and opens it in the browser.

I kept the search lanes explicit because the terms that surface a GRC role are different from the terms that surface RMF, SOC, IT support, or vendor-risk work.

The original prototype is in [`../prototype/job_finder_poc.py`](../prototype/job_finder_poc.py).

## 2. I changed the search strategy because the first one was too narrow

The first prototype emphasized common ATS domains such as Workday, Greenhouse, Lever, iCIMS, Taleo, and SmartRecruiters.

Testing showed that this worked, but it was not enough. For defense contractors in particular, company career pages and exact qualification phrases sometimes surfaced better low-years results than a strict ATS-only search.

That is why the second version added three modes:

```text
1. Strict ATS-only
2. Broad career sites
3. Exact low-years phrase search
```

The mode split was not added just to make the script more complicated. It came from comparing search results and seeing that one search pattern did not cover every employer well.

The current version is in [`../prototype/job_finder_modes_local.py`](../prototype/job_finder_modes_local.py), and the experiment trail is documented in [`search-experiments.md`](search-experiments.md).

## 3. Keep a human in the review loop

The prototype intentionally opens the search and lets me review the result before saving it.

That is because a search result can look promising while still being wrong for the actual target.

Examples from the search experiments included:

- a title containing `Principal` even though the snippet also contained lower-level qualification language
- a role that matched the experience requirement but was in the wrong location
- a broad career category page rather than an actual job posting
- a senior role that matched the topic but required far too much experience

So I did not want the first version making automatic "apply" decisions from title or snippet matches.

The local flow is deliberately:

```text
search
→ human review
→ record the result
```

rather than:

```text
search
→ assume match
→ apply
```

## 4. Start with CSV because the state model was simple

The first state store is a CSV with an explicit schema:

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

I chose CSV because I needed to prove the record structure and workflow, not build infrastructure.

At that stage, a database would have added setup and maintenance without solving a problem I actually had yet.

The useful question was:

```text
Can I reliably capture the fields I care about?
```

Once the answer was yes, I had a concrete state model that could move somewhere else later.

## 5. Move toward Google Sheets instead of adding a database

When I started connecting the workflow to Hermes Agent, I wanted state that was:

- structured
- persistent
- easy for an agent to read/write through an API
- easy for me to inspect and edit directly
- simple enough that I was not maintaining a database server just to track job rows

Google Sheets fits that stage of the project better than a database.

My reasoning is:

```text
CSV
→ proves the schema locally
→ but is tied to a local script/file

Google Sheets
→ keeps the table model
→ adds API access
→ remains directly human-readable/editable
```

I am not treating Sheets as a production database. If the project later needs concurrency control, relational joins, large-scale history, or stronger transactional guarantees, that would be evidence for moving to a real database. I do not need that complexity yet.

## 6. Use an API for state instead of automating spreadsheet clicks

If the agent needs to read or update structured state, I would rather call the Sheets API than make the browser click cells.

The API gives a clearer boundary:

```text
agent
→ authenticated request
→ spreadsheet range/value operation
→ returned state
```

That is easier to reason about and troubleshoot than UI automation for a spreadsheet.

It is also why the OAuth/Sheets troubleshooting matters in this project. The integration has distinct layers: credential discovery, authorization, scopes, API enablement, request formatting, and spreadsheet state.

## 7. Keep routine work local when possible

A major design goal is to avoid making every search, classification, or reasoning step depend on paid cloud-model tokens.

The direction I am aiming for is local-first:

```text
routine search/orchestration/classification
→ local agent/model where practical

important or uncertain decision
→ optional stronger cloud-model review/check
```

That is a design direction, not a claim that the full local/cloud review pipeline is finished today.

The reason is cost and control. If the agent is doing repetitive job-search work, I do not want every small step to require a metered API call when my own machine can handle routine work.

I still see value in a stronger cloud model as an occasional reviewer, especially for ambiguous job-fit or workflow decisions. I just do not want it to be the mandatory engine for every operation.

## 8. Keep consequential application actions human-controlled

The project can automate searching, organizing, and eventually some form-filling assistance, but there are points where I want an explicit stop.

The intended boundaries include:

- CAPTCHA
- MFA/passkeys
- legal attestations
- assessments
- factual questions the system cannot verify
- final application submission

The same rule applies to resume/application facts: the system must not invent experience, dates, employers, clearances, certifications, or skills.

This is not only a safety rule. It is also a data-quality rule. A job-search agent is not useful if it creates false application state.

## 9. Build the system in layers I can debug

The project has gradually become this:

```text
search construction
      ↓
manual result review
      ↓
structured state
      ↓
agent runtime
      ↓
OAuth / API integration
      ↓
future automation
```

That order is intentional.

If a search is bad, I can change the search logic.
If the state model is bad, I can change the schema.
If OAuth fails, I can debug OAuth without rewriting the search logic.
If an API request is malformed, I can fix the request without assuming authentication is broken.

The project is useful to me because each layer has a reason to exist and a failure mode I can inspect.