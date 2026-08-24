# HammDroid Job Agent

A local-first job-search automation project using **Hermes Agent**, a locally served language model, and the **Google Sheets API**.

The project is currently focused on proving the local-agent and Sheets integration before expanding into job discovery or application automation.

## Verified so far

- local Hermes agent running with a local language model
- Google OAuth authentication working
- Google Sheets API connected
- spreadsheet **create → write → read** round trip successfully tested
- general Google Drive browsing permission intentionally not granted

`append` behavior has not been separately validated, so it is not claimed here.

## Current architecture

```text
Human
  ↓
HammDroid / Hermes
  ↓
Local language model
  ↓
Google Sheets API
```

Google Sheets is intended to hold structured job-search state. Browser automation is a later layer for tasks that genuinely require a web application.

## Planned next work

- production job tracker
- job discovery and deduplication
- fit classification
- human approval queue
- one-job-at-a-time application assistance

Those pieces are planned, not presented as working features.

## Safety boundaries

The agent is designed to stop for:

- CAPTCHA
- MFA/passkeys or other authentication prompts
- legal attestations
- assessments
- unknown factual questions
- application submission

It must not invent employers, experience, dates, clearances, certifications, skills, or application answers. Coursework, labs, homelabs, and portfolio projects must not be represented as professional employment.

The agent also should not expand OAuth permissions, modify authentication, install alternate integrations, or change its environment merely because an approved operation failed.

## Google Sheets integration

The tested OAuth/API setup and the errors encountered while connecting it are documented in [Google Sheets Integration](docs/google-sheets-integration.md).

No OAuth client secrets, tokens, authorization codes, browser sessions, or other credentials are stored in this repository.
