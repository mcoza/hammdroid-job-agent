# Google Sheets Integration

This document records the Google Workspace integration work that is supported by the retained setup transcript. It focuses on the actual interfaces inspected during setup: OAuth client type, credential-path resolution, scopes, and redirect handling.

The repository does **not** contain OAuth secrets or tokens.

## Component path

```text
HammDroid workflow
      ↓
Hermes Agent runtime
      ↓
Google Workspace helper
      ↓
OAuth credential/token handling
      ↓
Google API
      ↓
spreadsheet state
```

Hermes and Google provide the runtime/API implementations. The project work represented here is the configuration and troubleshooting between those components.

## Desktop OAuth credential

The credential used in the setup transcript was an installed/Desktop OAuth client rather than a web-application credential.

The actual client ID and client secret are intentionally omitted from the repository.

The `.gitignore` excludes:

```text
client_secret*.json
google_client_secret.json
google_token.json
google_oauth_pending.json
credentials.json
token.json
.env*
.hermes/
```

## Credential-path troubleshooting

The most concrete integration failure in the retained transcript was not an authentication rejection. It was a path-resolution problem.

The client-secret JSON existed in the HammDroid project directory. It was copied to another Hermes-related directory, but a direct invocation of the Workspace setup helper still reported that no client secret was stored.

That led to inspection of the helper's path construction.

The setup code used logical paths equivalent to:

```python
CLIENT_SECRET_PATH = HERMES_HOME / "google_client_secret.json"
PENDING_AUTH_PATH = HERMES_HOME / "google_oauth_pending.json"
```

The standalone invocation in the retained session resolved the Hermes home under the user's normal home directory (`~/.hermes`), not the directory where the JSON had been copied.

The diagnostic chain was therefore:

```text
Desktop OAuth JSON exists
        ↓
setup helper says it cannot find a stored client secret
        ↓
inspect helper path resolution
        ↓
resolved CLIENT_SECRET_PATH differs from actual file location
```

This is a configuration/path failure, not evidence that the client secret itself was invalid.

A sanitized version of that trail is also kept in [`../evidence/google-oauth-debugging.md`](../evidence/google-oauth-debugging.md).

## Scope reduction

The stock Workspace helper exposed broader scopes than this project needed. The setup work moved toward a Sheets-focused set:

```python
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]
```

The intent was:

```text
spreadsheets
→ read/write spreadsheet contents through the Sheets API

drive.readonly
→ read-only Drive visibility needed by the chosen workflow
```

This removed the need to request Gmail, Calendar, Contacts, Docs, and full Drive scopes for HammDroid's job-tracking use case.

`drive.readonly` is still broad read-only Drive access. This repository does not describe it as single-file or zero-Drive access.

## Redirect-URI investigation

The retained setup transcript also captured a difference between the Desktop credential and the helper:

```text
credential redirect URI: http://localhost
helper redirect URI:     http://localhost:1
```

The session investigated whether Google's native-app localhost handling would accept the variation. The retained transcript contains conflicting intermediate reasoning and does not include the final token-exchange result.

For that reason, the repository records this as an **investigated configuration question**, not a confirmed root cause or confirmed fix.

## What the retained artifact proves

Directly supported by the retained setup transcript:

- Desktop OAuth credential was located and inspected
- credential lookup failed because the helper resolved a different path than expected
- Hermes home/path behavior was inspected
- the target Workspace scopes were reduced toward Sheets + read-only Drive
- the localhost redirect behavior was investigated

## What later notes say, but this artifact does not prove

Later project notes state that additional troubleshooting included:

- OAuth `403 access_denied`
- Sheets API `403 SERVICE_DISABLED`
- an HTTP 400 write-format error
- a spreadsheet create/write/read round trip

Those results are useful project history, but the raw request/response transcript was not recovered with the retained chat artifact used for this repository update. They are therefore **not treated as reproduced technical evidence here**.

If the underlying logs or script output are recovered later, they can be added without changing the project boundary.

## Current technical boundary

The retained evidence supports OAuth/setup integration work, not a custom Google Sheets client implementation.

What is not currently demonstrated in source:

- a repository-owned Sheets API wrapper
- append behavior
- schema migration/versioning
- concurrency handling
- duplicate detection
- automatic job discovery
- automatic application submission
