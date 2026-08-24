# HammDroid Job Agent

A local AI job-search assistant prototype built with **Hermes Agent**, an **Ollama-served local language model**, and the **Google Sheets API**.

The current implementation proves the local-agent and Sheets state layer. Job discovery and application automation are not presented as finished features.

## Working now

- Hermes running with a local language model
- Google OAuth authentication
- Google Sheets API integration
- spreadsheet **create → write → read** round-trip validation
- Sheets access without general Google Drive browsing permission

`append` behavior has not been separately validated.

## Current flow

```text
Human
  ↓
HammDroid / Hermes
  ↓
Ollama local model
  ↓
Google Sheets API
```

Google Sheets is used as the structured state layer rather than automating spreadsheet edits through a browser.

## What this project demonstrates

- configuring a local agent around a locally served model
- connecting a local workflow to Google Sheets through OAuth/API access
- diagnosing failures at the OAuth, API-service, request-format, and spreadsheet-operation layers
- limiting permissions and keeping consequential actions under human control

The tested integration and the real setup errors are documented in [Google Sheets Integration](docs/google-sheets-integration.md).

## Not yet claimed as working

- production job tracker
- automated job discovery or deduplication
- fit classification
- automated application workflow
- application submission

Hermes has browser tooling available, but this repository does not present a completed job-site automation pipeline.

## Safety boundaries

The agent is intended to stop for CAPTCHA, MFA/passkeys, legal attestations, assessments, unknown factual questions, and application submission. It must not invent employers, experience, dates, clearances, certifications, skills, or application answers.

Coursework, labs, homelabs, and portfolio projects must not be represented as professional employment.

No OAuth client secrets, tokens, authorization codes, browser sessions, or other credentials are stored in this repository.