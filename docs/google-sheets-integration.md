# Google Sheets Integration

I added Google Sheets because I needed somewhere simple to keep job-search state that both HammDroid and I could access.

I did not want to add a database before I actually needed one. Sheets gives me rows and columns, API access, and a UI I can open myself if I want to check or fix something.

## Setup

```text
Hermes Agent
    ↓
Google Workspace helper
    ↓
OAuth 2.0
    ↓
Google Sheets API
    ↓
spreadsheet
```

The Google side is separate from the local model side. Ollama can be working while Google authentication is broken, and Google authentication can be working while the Sheets request itself is wrong.

That ended up mattering while I was troubleshooting it.

## Credential path

At first the OAuth client file existed on the machine, but Hermes was not looking in the place where I had put it.

The helper expected the file under the Hermes home directory:

```text
%USERPROFILE%\.hermes\google_client_secret.json
```

That was a path problem, not a bad OAuth client.

The useful lesson was simple: a file existing somewhere does not mean the program is reading that location.

OAuth tokens and pending authorization files also stay under the local Hermes setup instead of going into Git.

## OAuth client

I used a Google Desktop OAuth client.

The basic flow was:

```text
client config
→ Google sign-in and consent
→ localhost callback
→ token exchange
→ stored token
→ Google API request
```

A browser error on the localhost callback did not automatically mean the whole authorization failed. What mattered was whether the helper received the authorization response it needed.

Authorization codes and callback URLs containing codes are not kept in the repo.

## Permissions

I did not want HammDroid asking for Gmail, Calendar, Contacts, or Docs permissions when this part of the project only needed spreadsheet access.

The reduced scope direction used here was:

```text
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/drive.readonly
```

`spreadsheets` allows spreadsheet read and write access.

`drive.readonly` is still general read-only Drive access, so I do not describe the setup as having no Drive access. The workflow is meant to stay on the job-tracking sheet even though the scope itself is broader than one file.

## Problems I hit

### OAuth access denied

One authorization attempt returned:

```text
403 access_denied
```

The OAuth app was still in testing mode and the account needed to be added as a test user.

That was an OAuth setup issue, not a Sheets request problem.

### Sheets API disabled

After OAuth was working, a request returned:

```text
HTTP 403
SERVICE_DISABLED
service=sheets.googleapis.com
```

The Google Cloud project did not have the Sheets API enabled yet.

Enabling `sheets.googleapis.com` fixed that part without changing the OAuth setup.

### Bad write request

A later write returned HTTP 400 because the range and value request was formatted incorrectly.

At that point authentication was already working. The problem was the request itself.

The errors ended up mapping pretty cleanly:

```text
403 access_denied
→ OAuth setup

403 SERVICE_DISABLED
→ Google Cloud API setting

HTTP 400
→ bad request format
```

## What I tested

The final test was small on purpose:

```text
create spreadsheet
→ write known values
→ read the values back
```

That worked after the earlier problems were fixed.

It was enough to prove that HammDroid could use authenticated Google Sheets access for state.

I have not separately tested append behavior yet.

## Why I use the API instead of browser clicks

If HammDroid needs to update the sheet, the API is easier for me to follow than automating clicks in the Google Sheets website.

With the API I can check:

- whether OAuth worked
- which permissions were granted
- whether the API is enabled
- whether the request is valid
- what data came back

Browser automation would add selectors, page state, timing, and rendering problems to something that already has an API.

## Secrets and local files

The repo does not store:

- OAuth client-secret files
- access or refresh tokens
- pending OAuth state
- authorization codes
- `.env` files
- browser sessions
- local Hermes state

Those files stay local and are covered by `.gitignore`.

## Current status

Tested or configured:

- Google Desktop OAuth client
- Hermes credential path
- OAuth test-user fix
- Sheets API enabled
- malformed write request identified and fixed
- spreadsheet create, write, and read test

Not finished:

- append testing
- final job-tracking sheet design
- deduplication
- multiple writers
- automatic job ingestion
- full application workflow
