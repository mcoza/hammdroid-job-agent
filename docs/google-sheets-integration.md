# Google Sheets Integration

This documents the **tested** Google Sheets integration for HammDroid: OAuth authentication, API activation, and a small create/write/read validation.

## Why Sheets

Google Sheets is being used as a lightweight structured state layer for job-search data instead of driving the spreadsheet through browser automation.

```text
Hermes / HammDroid
        ↓
Google Sheets API
        ↓
structured job state
```

## Tested result

The end-to-end validation was intentionally small:

1. create a temporary spreadsheet
2. write known values
3. read the same values back

The create → write → read test succeeded after the Sheets API was enabled.

`append` behavior has **not** been separately validated.

## OAuth scope

The tested setup grants Google Sheets access without general Google Drive browsing access.

```text
Google Sheets access      allowed
General Drive browsing    not granted
Gmail                     not granted
Calendar                  not granted
Contacts                  not granted
Docs                       not granted
```

The Sheets scope is broader than one spreadsheet, so normal agent behavior is still restricted to the intended job tracker.

## Problems encountered

### OAuth test-user access

An early authorization attempt returned `403 access_denied` while the OAuth app was in testing mode.

The authorizing account needed to be listed as a test user.

### Localhost callback

The Desktop OAuth flow redirected to localhost. A browser page failing to load did not necessarily mean authorization had failed; the callback URL still contained the authorization response needed by the OAuth helper.

Authorization codes and callback URLs containing codes are not stored in this repository.

### Sheets API disabled

The first spreadsheet-create request returned:

```text
HTTP 403
SERVICE_DISABLED
service=sheets.googleapis.com
```

That showed authentication was working but the Google Sheets API itself was disabled for the Cloud project. Enabling the API fixed that issue without changing OAuth scopes.

### Malformed write request

A later write returned HTTP 400 because the requested range/value shape was malformed. That was a request-format issue rather than an authentication problem.

## Troubleshooting lesson

These failures were useful because they occurred at different layers:

```text
OAuth authorization
      ↓
API enabled/disabled state
      ↓
request formatting
      ↓
spreadsheet operation
```

Treating every failure as an authentication problem would have led to unnecessary reconfiguration.

## Security

Do not commit:

- OAuth client JSON files
- token or refresh-token files
- authorization codes
- callback URLs containing codes
- `.env` secrets
- browser profiles/session cookies

This repository documents the integration behavior, not the credentials used to authorize it.
