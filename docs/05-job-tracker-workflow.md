# 05 — Job Tracker Workflow

Google Sheets is the authoritative queue and state store for the job-search workflow.

## Planned columns

| Field | Purpose |
|---|---|
| Date Found | Discovery date |
| Job Title | Posted role |
| Company | Employer |
| Location | Job location |
| Work Arrangement | On-site / hybrid / remote |
| Salary / Pay | Compensation when available |
| Experience Required | Stated experience requirement |
| Required Qualifications | Hard requirements |
| Preferred Qualifications | Nice-to-have requirements |
| Fit Rating | STRONG APPLY / APPLY / STRETCH |
| Short Fit Reason | Concise rationale |
| Active Status | VERIFIED / UNVERIFIED |
| Source | Job source |
| Job URL | Listing URL |
| Application URL | Direct application URL |
| Status | NEW / APPROVED / APPLIED / etc. |

## Discovery flow

```text
Search
  ↓
Extract listing
  ↓
Apply hard filters
  ↓
Deduplicate
  ↓
Evaluate fit
  ↓
Verify active status
  ↓
Write retained job to Sheet
```

## Hard filters

Examples of deterministic filters that should run before fuzzy model judgment:

- duplicate URL → skip
- same company/title/location already tracked → skip duplicate
- clearly outside location constraints → skip
- clearly closed/expired/removed → skip
- senior/principal/manager/director roles → normally skip
- roles requiring substantially more experience than the target profile → normally skip

## Fit classes

### STRONG APPLY

Requirements align closely with the candidate profile and there are no major blockers.

### APPLY

Reasonable match with manageable gaps, especially when missing items are preferred rather than required.

### STRETCH

A meaningful mismatch exists, but the role is still plausible enough to justify human review.

### SKIP

Obvious mismatch. SKIP items should generally not clutter the primary review queue.

## Human approval flow

```text
NEW
 ↓
Human review
 ├── REJECTED
 └── APPROVED
       ↓
    Apply Mode
       ↓
    APPLIED
```

The human decides whether a retained job moves into Apply Mode.

## Apply Mode

Apply Mode should process one approved job at a time.

Safe automation includes:

- opening the approved listing
- identifying form fields
- filling known factual information
- selecting the correct approved resume
- preparing the application for review

Stop and escalate for:

- CAPTCHA
- MFA/passkeys
- legal attestations
- assessments
- unclear questions
- unknown factual information
- ambiguous experience or eligibility questions

## Submission boundary

The agent must never submit an application without explicit human authorization.

## Future improvements

- reviewer/critic pass for borderline listings
- automatic status metrics
- source quality tracking
- stale-listing rechecks
- application follow-up tracking
- duplicate detection across aggregators and employer career pages
