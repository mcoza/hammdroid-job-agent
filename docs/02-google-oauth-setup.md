# 02 — Google OAuth Setup

This guide documents the one-time Google OAuth setup used to let Hermes access Google Sheets through the API.

## 1. Create a Google Cloud project

Create a dedicated Google Cloud project for the agent integration.

A dedicated project keeps OAuth configuration and API enablement separate from unrelated work.

## 2. Configure Google Auth Platform

Configure the OAuth consent screen.

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

## 3. Create an OAuth client

Create an OAuth 2.0 client with:

```text
Application type: Desktop app
```

Download the client JSON.

Do not commit it to GitHub.

## 4. Set the Hermes home

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

The client should be copied into the configured Hermes credential area.

## 6. Generate the authorization URL

```powershell
& "<HERMES_INSTALL>\venv\Scripts\python.exe" `
  "<HERMES_INSTALL>\skills\productivity\google-workspace\scripts\setup.py" `
  --auth-url
```

Open the generated Google authorization URL in a browser.

## 7. Grant only the permissions you intend to use

For this project, Google Sheets access was granted while general Google Drive browsing was declined.

The intended permission model is:

```text
Google Sheets access      allowed
General Drive browsing    not granted
Gmail                     not granted
Calendar                  not granted
Contacts                  not granted
Docs                      not granted
```

## 8. Handle the localhost callback

The desktop OAuth flow may redirect to a localhost address that does not load successfully in the browser.

That does not necessarily mean OAuth failed.

If the callback URL contains the authorization response, copy the complete callback URL and provide it to the Hermes OAuth helper.

Do not paste callback URLs containing authorization codes into public chats, logs, issues, or repositories.

## 9. Exchange the authorization response

Example pattern:

```powershell
& "<HERMES_INSTALL>\venv\Scripts\python.exe" `
  "<HERMES_INSTALL>\skills\productivity\google-workspace\scripts\setup.py" `
  --auth-code "<FULL_CALLBACK_URL>"
```

A successful exchange should produce a valid token in the configured Hermes credential area.

## 10. Verify authentication

```powershell
& "<HERMES_INSTALL>\venv\Scripts\python.exe" `
  "<HERMES_INSTALL>\skills\productivity\google-workspace\scripts\setup.py" `
  --check
```

A partial-scope warning is not automatically an authentication failure. It can simply mean you intentionally declined permissions the bundled Workspace integration also knows how to use.

## Security notes

Never commit or publish:

- OAuth client JSON files
- token files
- refresh tokens
- authorization codes
- callback URLs containing codes
- `.env` files containing secrets
