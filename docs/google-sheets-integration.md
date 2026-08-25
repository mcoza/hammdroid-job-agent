# Google Sheets Integration

The reason I added Google Sheets was not "because agent projects need a database." It was the opposite: I wanted persistent structured state without adding a database before I had a database-sized problem.

Sheets gives HammDroid a table the agent can access through an API while I can still open it directly and see or correct the same state.

## Architecture

The integration path I configured is:

```text
Hermes Agent
    ↓
Google Workspace helper
    ↓
OAuth 2.0 credentials / token
    ↓
Google Sheets API
    ↓
spreadsheet state
```

The Google API integration is separate from the local LLM runtime. Ollama/Hermes can be working while Google authentication is broken, and Google authentication can be working while a Sheets request is malformed.

That separation became important during troubleshooting.

## Credential location

The OAuth client file originally existed in the project area, but the Hermes helper was resolving credentials from the Hermes home directory instead.

The logical location used by the helper was:

```text
%USERPROFILE%\.hermes\google_client_secret.json
```

Token/pending-auth state was also handled under the local Hermes home rather than committed to the repository.

The useful distinction was:

```text
credential file exists
≠
application is reading that path
```

So the troubleshooting step was to identify where the helper actually resolves its credential files before changing the OAuth client itself.

## OAuth client type

I used a Google **Desktop / installed application** OAuth client.

The flow is conceptually:

```text
client configuration
      ↓
authorization request
      ↓
Google consent screen
      ↓
localhost callback / authorization response
      ↓
token exchange
      ↓
stored token
      ↓
authenticated Google API call
```

A localhost browser error was not automatically proof that authorization had failed. What mattered was whether the authorization response had been returned in a form the helper could consume.

Authorization codes and callback URLs containing codes are treated as credentials and are not stored in this repository.

## Scope decision

I did not want HammDroid requesting unrelated Gmail, Calendar, Contacts, or Docs permissions just because the Google Workspace tooling could support them.

The reduced scope direction used for this workflow was:

```text
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/drive.readonly
```

That means:

```text
spreadsheets   → read/write spreadsheet content
drive.readonly → read-only Drive access
```

`drive.readonly` is still broader than access to one spreadsheet, so I do not describe this as "no Drive access." The workflow is intended to operate on the designated job-tracking sheet even though the OAuth scope itself permits read-only Drive visibility.

## Failure 1 — OAuth `403 access_denied`

An early authorization attempt returned:

```text
403 access_denied
```

The OAuth app was still in testing mode and the account performing authorization needed to be included as a test user.

That placed the failure here:

```text
OAuth consent/test-user configuration
```

not in the Sheets request code.

## Failure 2 — Sheets API not enabled

After OAuth was working, a spreadsheet request returned:

```text
HTTP 403
SERVICE_DISABLED
service=sheets.googleapis.com
```

That was useful evidence because it meant the request had progressed farther than the earlier OAuth failure.

The failing layer was now:

```text
Google Cloud project
→ Sheets API service enablement
```

Enabling `sheets.googleapis.com` corrected that layer without rebuilding the OAuth setup.

## Failure 3 — malformed write request

A later write failed with HTTP 400 because the range/value request shape was malformed.

Again, that was a different subsystem:

```text
HTTP 400
→ request construction / range-value shape
```

Reauthorizing OAuth would not have fixed it.

This gave me a useful failure map:

```text
403 access_denied
→ authorization / consent

403 SERVICE_DISABLED
→ Cloud API enablement

400 malformed request
→ request formatting
```

## Validation

The small end-to-end test was deliberately limited:

```text
create spreadsheet
→ write known values
→ read values back
```

That create → write → read path succeeded after the earlier integration problems were corrected.

This was enough to prove that Hermes could use authenticated Google API access as a state path for the project.

`append` behavior was **not separately validated**, so I do not claim it as tested functionality.

## Why API state instead of spreadsheet browser automation

I would rather have HammDroid update state through an API than click through the Google Sheets UI.

With the API, I can reason about:

```text
authentication
→ scope
→ service availability
→ request body/range
→ returned data
```

Those are inspectable technical boundaries. Browser-driving spreadsheet cells would add UI state, selectors, timing, and rendering failures to a problem that already has a structured API.

## Security boundary

The repository excludes local runtime credentials and session state, including:

- OAuth client-secret JSON
- access/refresh token files
- pending OAuth state
- authorization codes
- `.env` files
- browser profile/session artifacts
- local Hermes state

The source repository documents the integration. It is not the credential store.

## Current status

Validated/configured:

- Google Desktop OAuth client flow
- Hermes credential-path resolution
- OAuth test-user issue identified
- Sheets API service enabled
- malformed write request isolated from authentication
- spreadsheet create → write → read round trip

Not claimed as complete:

- append validation
- production schema/versioning
- deduplication logic
- concurrent writers
- end-to-end job ingestion
- autonomous application workflow
