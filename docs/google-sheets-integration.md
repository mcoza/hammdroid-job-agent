# Google Sheets Integration

The goal was simple: move HammDroid's job-tracking state beyond a local CSV without adding a database.

Hermes Agent was used as the external runtime and its Google Workspace tooling handled the Google API side.

## What was tested

- Google Desktop OAuth client setup
- Sheets-focused authorization
- spreadsheet create → write → read round trip

Append was not separately validated.

## Troubleshooting trail

### 1. Credential existed, but the helper could not find it

The OAuth JSON was present on disk, but the standalone Workspace helper resolved its credential path from the Hermes home directory rather than the project directory.

The useful lesson was:

```text
file exists
≠
application is looking in that location
```

Tracing `HERMES_HOME` / the helper's path resolution identified the mismatch.

### 2. OAuth access was blocked

A `403 access_denied` response was traced to the Google OAuth consent/test-user layer rather than to the spreadsheet request itself.

### 3. Authentication worked, but the API was disabled

A later request returned `403 SERVICE_DISABLED` for `sheets.googleapis.com`.

That separated two different conditions:

```text
valid OAuth token
≠
Google Sheets API enabled for the project
```

Enabling the Sheets API moved the failure to the request layer.

### 4. The write request was malformed

The next failure was an HTTP 400 caused by the shape of the Sheets write request. Correcting the range/value structure allowed the write to succeed.

The final test was:

```text
create spreadsheet
→ write values
→ read values back
```

That was enough to validate the state-storage direction for the prototype.

## Security boundary

The repository does not contain OAuth client secrets, access/refresh tokens, authorization codes, or local Hermes credential files. Those are excluded by `.gitignore`.

The project also reduced the Workspace access requested for this workflow rather than keeping unrelated Gmail, Calendar, Contacts, or Docs permissions.

## Not claimed

This repository does not contain a custom Google API client, production database layer, automatic job ingestion pipeline, or autonomous application workflow.
