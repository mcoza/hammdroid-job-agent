# Google OAuth / Hermes Integration Evidence

This is a sanitized reconstruction from the retained setup transcript. Secrets, client IDs, authorization codes, tokens, and user-specific home paths are intentionally omitted.

## 1. Desktop OAuth credential identified

The Google credential file used during setup had the `installed` application shape expected for a Desktop OAuth client.

The credential itself is **not** stored in this repository.

## 2. Credential lookup failed even though the file existed

The client-secret file originally existed in the HammDroid project directory. It was then copied to another Hermes-related directory, but running the Google Workspace setup helper still returned the equivalent of:

```text
No client secret stored.
```

That changed the troubleshooting question from:

```text
Is the JSON valid?
```

to:

```text
Which path is the helper actually resolving?
```

The setup code used logical paths such as:

```python
CLIENT_SECRET_PATH = HERMES_HOME / "google_client_secret.json"
PENDING_AUTH_PATH = HERMES_HOME / "google_oauth_pending.json"
```

Inspecting the helper's home-resolution behavior showed that the standalone invocation was resolving its credential path under the user's Hermes home (`~/.hermes`) rather than the directory where the file had been copied.

The practical lesson was:

```text
credential exists on disk
        ≠
application is looking in that directory
```

## 3. Scope reduction

The stock Google Workspace helper exposed broader Workspace scopes than HammDroid needed. The project goal was to keep the integration focused on spreadsheet state rather than Gmail, Calendar, Contacts, Docs, or full Drive access.

The reduced target used during the setup work was:

```python
SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]
```

The reason for keeping `drive.readonly` was to retain read-only Drive visibility while allowing Sheets read/write operations through the Sheets scope. This is still broader than access to one single spreadsheet, so the repository does not describe it as zero Drive access.

## 4. Redirect-URI investigation

The retained transcript also captured a mismatch worth investigating:

```text
Desktop credential redirect URI: http://localhost
helper redirect URI:             http://localhost:1
```

The session contained conflicting reasoning about whether Google's native-app localhost handling would accept the port variation. Because the retained artifact does not contain the completed token-exchange result, this repository treats the redirect issue as **investigated but unresolved in the retained evidence** rather than claiming a confirmed fix.

## Evidence boundary

The retained transcript directly supports:

- the use of a Desktop OAuth credential
- credential-path troubleshooting
- inspection of Hermes home/path resolution
- reduction of requested Workspace scopes toward Sheets + read-only Drive
- investigation of the localhost redirect behavior

Later project notes describe additional Sheets API troubleshooting and a create/write/read test, but the retained artifact available for this repository does not contain the underlying request/response transcript. Those later results are therefore not presented here as reproduced evidence.
