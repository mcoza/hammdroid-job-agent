# Google Sheets Integration

This documents the Google Sheets integration tested for HammDroid: Desktop OAuth setup, Hermes credential-file handling, API activation, request troubleshooting, and a small spreadsheet create/write/read validation.

The goal is to use Sheets as a structured state layer that both a human and the agent can inspect, rather than automating spreadsheet edits through browser clicks.

## Component path

```text
Hermes workflow
      ↓
Google Workspace skill/helper
      ↓
OAuth 2.0 credentials + stored token
      ↓
Google Sheets API
      ↓
spreadsheet state
```

The repository does not contain Google credentials or tokens. It documents how the integration behaved and what was tested.

## Credential and token files

The Hermes Google Workspace helper uses logical files under the Hermes home directory:

```text
google_client_secret.json  → OAuth Desktop client configuration
google_oauth_pending.json  → temporary authorization-flow state
google_token.json          → token / refresh-token state after authorization
```

The project `.gitignore` excludes all of these names.

The tested OAuth client was a Google **Desktop / installed application** client rather than a web-application client.

## OAuth flow

The practical flow was:

```text
Desktop client JSON
      ↓
Hermes setup helper generates authorization request
      ↓
Google consent screen
      ↓
localhost callback / authorization response
      ↓
token exchange
      ↓
google_token.json
      ↓
authenticated API requests
```

A browser error at the localhost callback did not automatically mean the OAuth flow failed. The callback URL could still contain the authorization response expected by the helper.

Authorization codes and callback URLs containing codes are treated as credentials and are not stored in this repository.

## Scope work

The stock Google Workspace skill exposed broader Google Workspace scopes than HammDroid needed. The setup work narrowed the target to Sheets plus read-only Drive access rather than Gmail, Calendar, Contacts, Docs, or full Drive access.

The intended reduced set was:

```text
https://www.googleapis.com/auth/spreadsheets
https://www.googleapis.com/auth/drive.readonly
```

Important distinction:

```text
spreadsheets   → read/write spreadsheet contents through the Sheets API
drive.readonly → read-only Drive access; this is still broader than one spreadsheet
```

So this repository does **not** claim that there is zero general Drive visibility. `drive.readonly` is a read-only Drive scope. The operational workflow is still intended to stay on the designated job-tracking sheet.

Gmail, Calendar, Contacts, and Docs scopes were intentionally excluded from the reduced configuration.

## Tested spreadsheet round trip

The smallest useful integration test was:

```text
create temporary spreadsheet
        ↓
write known values
        ↓
read values back
        ↓
compare returned state with expected state
```

The create → write → read round trip is documented as successful after the Sheets API was enabled.

`append` has **not** been separately validated, so the repository does not claim append behavior as completed functionality.

## Failure 1: OAuth app in testing mode

An early authorization attempt returned:

```text
HTTP 403
access_denied
```

The OAuth consent configuration was still in testing mode, and the account performing the authorization had to be added as a test user.

The useful diagnostic distinction was:

```text
OAuth consent denied before token issuance
→ inspect OAuth app/test-user configuration
```

rather than changing spreadsheet request code.

## Failure 2: credential path resolution

The Google Workspace helper resolves credential files from the Hermes home directory. During setup, the client-secret JSON initially existed in the HammDroid project directory while the helper was looking under its Hermes credential directory.

That produced a path/state problem rather than a bad OAuth client.

The troubleshooting question became:

```text
credential file exists somewhere
≠ helper is reading that location
```

The fix was to place the client configuration where the helper actually resolves `google_client_secret.json`.

This is one reason credentials are kept outside the Git repository: runtime secret storage and source-code storage are separate concerns.

## Failure 3: Sheets API disabled

The first spreadsheet-create attempt returned:

```text
HTTP 403
SERVICE_DISABLED
service=sheets.googleapis.com
```

That identified the failing layer as the Google Cloud project's service configuration. The request reached Google, but the Sheets API was not enabled for the project.

Enabling `sheets.googleapis.com` resolved this layer without redesigning the OAuth flow.

```text
OAuth/client setup
      ↓
request reaches Google API
      ↓
SERVICE_DISABLED
      ↓
enable Sheets API in the Cloud project
```

## Failure 4: malformed write request

A later write attempt returned HTTP 400 because the requested range/value shape was malformed.

That is a different class of failure from OAuth or API activation:

```text
400 malformed request
→ inspect range / request-body shape

403 access_denied
→ inspect authorization/consent

403 SERVICE_DISABLED
→ inspect Cloud API enablement
```

This distinction matters because repeatedly reauthorizing OAuth would not fix a malformed Sheets request.

## Troubleshooting model from the integration

The setup became easier once the integration was treated as layers:

```text
1. credential discovery
2. OAuth consent / token acquisition
3. OAuth scopes
4. Google Cloud API enablement
5. request construction
6. spreadsheet operation
7. returned spreadsheet state
```

A failure at one layer should be investigated there before reconfiguring layers that have already been demonstrated to work.

## Security controls used in the repo

The repository excludes:

- OAuth client-secret JSON files
- token and refresh-token files
- pending OAuth state files
- authorization codes
- callback URLs containing codes
- `.env` files
- browser profiles/session cookies

The `.gitignore` is part of the project design because credential handling is an integration concern, not just a documentation note.

## Current boundary

Validated or documented as working:

- Desktop OAuth client setup
- token-based Google API access
- Sheets API activation
- create/write/read spreadsheet round trip
- failure isolation across OAuth, service-enable, and request-format layers

Not yet claimed:

- append validation
- schema migration/versioning
- concurrency handling
- duplicate detection
- automated job discovery
- automated application submission
