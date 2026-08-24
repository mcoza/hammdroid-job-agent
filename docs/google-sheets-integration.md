# Google Sheets Integration

This document covers the one-time OAuth setup, API activation, validation test, and the important errors encountered while connecting HammDroid to Google Sheets.

## Why Sheets

Google Sheets is used as the job-state layer so HammDroid can store and update structured job data without clicking through the spreadsheet UI.

The intended split is:

```text
API  -> state, tracking, updates
Browser -> application sites and tasks that genuinely require a browser
```

## 1. Create a Google Cloud project

Create a dedicated Google Cloud project for the agent integration. This keeps OAuth configuration and API enablement separate from unrelated work.

## 2. Configure Google Auth Platform

For a private personal integration:

- set the application name
- provide a support email
- use an **External** audience if required for the account type
- keep the application in **Testing** while developing
- add the Google account that will authorize the integration as a **Test user**

If the account is not added as a test user, Google may return:

```text
Error 403: access_denied
```

with a message saying the application has not completed verification.

## 3. Create a Desktop OAuth client

Create an OAuth 2.0 client with:

```text
Application type: Desktop app
```

Download the client JSON and keep it out of the repository.

## 4. Point Hermes at its credential home

Hermes derives its credential location from `HERMES_HOME` when that environment variable is available.

Example:

```powershell
$env:HERMES_HOME = "E:\AI\Hermes"
```

For a persistent Windows user environment variable:

```powershell
[Environment]::SetEnvironmentVariable("HERMES_HOME","E:\AI\Hermes","User")
```

Use paths appropriate for your own installation.

## 5. Store the OAuth client through Hermes

Use the Python interpreter from the Hermes virtual environment rather than installing another Python runtime just for this step.

Example pattern:

```powershell
& "<HERMES_INSTALL>\venv\Scripts\python.exe" `
  "<HERMES_INSTALL>\skills\productivity\google-workspace\scripts\setup.py" `
  --client-secret "<PATH_TO_DOWNLOADED_CLIENT_JSON>"
```

## 6. Generate the authorization URL

```powershell
& "<HERMES_INSTALL>\venv\Scripts\python.exe" `
  "<HERMES_INSTALL>\skills\productivity\google-workspace\scripts\setup.py" `
  --auth-url
```

Open the generated Google authorization URL in a browser.

## 7. Grant only the permissions you intend to use

For this project, Google Sheets access was granted while general Google Drive browsing was declined.

```text
Google Sheets access      allowed
General Drive browsing    not granted
Gmail                     not granted
Calendar                  not granted
Contacts                  not granted
Docs                       not granted
```

The Sheets OAuth scope is still broader than a single spreadsheet, so HammDroid also has a behavioral rule restricting normal operation to the designated job tracker.

## 8. Handle the localhost callback

The Desktop OAuth flow may redirect to a localhost address that does not load successfully in the browser.

That does not necessarily mean OAuth failed. If the callback URL contains the authorization response, provide the complete callback URL to the Hermes OAuth helper.

Do not publish callback URLs containing authorization codes.

Example exchange:

```powershell
& "<HERMES_INSTALL>\venv\Scripts\python.exe" `
  "<HERMES_INSTALL>\skills\productivity\google-workspace\scripts\setup.py" `
  --auth-code "<FULL_CALLBACK_URL>"
```

## 9. Verify authentication

```powershell
& "<HERMES_INSTALL>\venv\Scripts\python.exe" `
  "<HERMES_INSTALL>\skills\productivity\google-workspace\scripts\setup.py" `
  --check
```

A partial-scope warning is not automatically an authentication failure. It can mean the user intentionally declined permissions the bundled Workspace integration also knows how to use.

## 10. Enable the Google Sheets API

OAuth and API activation are separate controls.

The first create request returned:

```text
HTTP 403
SERVICE_DISABLED
service=sheets.googleapis.com
```

That meant:

```text
OAuth authentication       working
Token loading              working
Request reached Google     working
Sheets API service         disabled
```

The correct fix was to enable **Google Sheets API** in the same Cloud project and retry the same operation. No new OAuth flow or framework modification was required.

## 11. Validate create -> write -> read

The end-to-end test was deliberately small:

1. create a temporary spreadsheet
2. write known values
3. read the same values back

Example range:

```text
A1:A2
```

Example values:

```text
test_value_1
test_value_2
```

Expected logical read-back:

```json
[
  ["test_value_1"],
  ["test_value_2"]
]
```

The test passed after the API was enabled.

## Errors encountered

### OAuth app not verified

**Symptom:** `403 access_denied`

**Cause:** the OAuth app was in Testing mode and the authorizing account was not listed as a test user.

**Fix:** add the account under **Audience / Test users**.

### Browser blocks localhost callback

**Meaning:** the page failing to load does not automatically mean OAuth failed. The authorization response may still be present in the callback URL.

### `SERVICE_DISABLED`

**Meaning:** OAuth is valid, but `sheets.googleapis.com` is disabled for the Cloud project.

**Fix:** enable Google Sheets API and retry the same request.

### HTTP 400 on a write

Spreadsheet creation succeeded, but one write request returned HTTP 400 because the requested range/value shape was malformed.

This was a request-format problem, not an authentication problem.

### Missing Drive scope

The token was valid but did not include general Drive read access. That was intentional.

A failed Drive cleanup operation was not treated as a reason to expand OAuth permissions. The one-time test spreadsheet could be deleted manually instead.

## Security notes

Never commit or publish:

- OAuth client JSON files
- token files
- refresh tokens
- authorization codes
- callback URLs containing codes
- `.env` files containing secrets
- browser profiles or session cookies

The important runtime token should be treated as more sensitive than the downloaded Desktop OAuth client definition because it represents the account authorization granted to the application.
