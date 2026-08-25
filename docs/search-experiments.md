# Search Strategy Experiments

The Python search modes were not chosen arbitrarily. I tested several search patterns and used the results to decide what the next version of the script needed.

The point of these experiments was to answer:

```text
Which search pattern actually surfaces low-years cybersecurity roles reliably?
```

## 1. Strict ATS-only search

Example pattern:

```text
site:myworkdayjobs.com "Northrop Grumman" "Cybersecurity Analyst" "0 years"
```

This worked and returned real Workday-hosted Northrop Grumman results.

That proved ATS-targeted searches were useful, but not that ATS-only was sufficient.

## 2. Company career-domain search

Example pattern:

```text
site:jobs.northropgrumman.com/careers/job "Northrop Grumman" "Master's degree with 0 years" "Cybersecurity Analyst"
```

This surfaced useful low-years roles that were not necessarily easier to find through the strict ATS-only pattern.

That changed the design from one fixed site filter to multiple search modes.

## 3. Exact qualification-phrase search

Example:

```text
"Bachelor's degree with 0 years" "Northrop Grumman" "Cybersecurity Analyst"
```

This found associate/pathways-style roles.

That mattered because titles alone were not enough. Qualification language can reveal early-career openings even when the title vocabulary varies.

## 4. Broad career-category search

Example:

```text
site:careers.leidos.com "Information Assurance" jobs
```

This found useful category pages, but category pages were less useful than exact posting pages for deciding whether a specific role was worth reviewing.

So broad category discovery can help find an employer's role family, but it is weaker evidence than an actual posting.

## What the result review taught me

The saved experiment results also showed why human review still matters.

Examples included:

```text
Principal title
+ snippet containing lower-level qualification language
→ search matched, but title still makes it a weak fit

Strong low-years qualification
+ wrong geographic location
→ technically relevant, operationally not useful

Senior role
+ correct cybersecurity topic
→ search matched the subject, but experience requirement made it a skip
```

The search engine can retrieve candidates. It does not automatically understand the full suitability decision.

## Resulting search design

The experiment led to the current modes:

```text
Strict ATS-only
→ useful when a known ATS hosts the employer's jobs

Broad career sites
→ useful when employer-hosted career pages outperform ATS-only discovery

Exact low-years phrase
→ useful when education/experience language is more reliable than title wording
```

The current script combines those modes with:

- role-lane terms
- location terms
- low-years experience phrases
- title exclusions such as `-senior -principal -director`

## Takeaway

The important design change was:

```text
first idea: one broad query should be enough

observed results: different employers expose jobs differently

current approach: choose a search mode based on what kind of source/qualification evidence I want
```

That is why `job_finder_modes_local.py` has separate search modes rather than one increasingly large query string.