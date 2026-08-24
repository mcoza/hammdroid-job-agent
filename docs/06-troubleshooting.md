# 06 — Troubleshooting Notes

This page records the important failure modes encountered during setup and what they actually meant.

## Error: OAuth app not verified

### Symptom

```text
Error 403: access_denied
```

Google says the app has not completed verification and can only be accessed by developer-approved testers.

### Cause

The OAuth app is in Testing mode and the authorizing Google account is not listed as a test user.

### Fix

Add the account under the OAuth application's **Audience / Test users** section.

Do not switch to a different OAuth client type just because this error appears.

---

## Error: browser blocks localhost callback

### Symptom

The browser refuses to load the localhost callback address after Google authorization.

### Meaning

The browser error does not automatically mean OAuth failed. Desktop OAuth flows may still place the authorization response in the callback URL.

### Fix

Use the complete callback URL with the Hermes OAuth helper as designed.

Never publish a callback URL containing an authorization code.

---

## Error: `SERVICE_DISABLED`

### Symptom

```text
HTTP 403
SERVICE_DISABLED
service=sheets.googleapis.com
```

### Cause

OAuth is valid, but the Google Sheets API itself is disabled for the Google Cloud project.

### Fix

Enable **Google Sheets API** and repeat the same test.

Do not rebuild OAuth or patch the framework.

---

## Error: HTTP 400 on a Sheets write

### Symptom

Spreadsheet creation succeeds, but a write operation returns HTTP 400.

### Likely cause

The requested range does not match the shape of the values being supplied.

### Fix

Check the range and the row/column layout of the value array.

Example:

```text
Range: A1:A2
Values:
  row 1 -> test_value_1
  row 2 -> test_value_2
```

An HTTP 400 at this stage does not automatically indicate an OAuth problem.

---

## Warning: token missing Drive scope

### Symptom

Authentication is reported as valid but partial because a Drive-related scope is absent.

### Meaning

This can be intentional. The user may have granted Sheets access while declining general Drive access.

### Response

Do not automatically start a new OAuth flow or request broader permissions. First determine whether the required Sheets operation actually needs the missing scope.

---

## Problem: agent keeps triggering login/passkey prompts

### Cause

The agent has left the intended API path and is attempting interactive authentication or browser-based recovery.

### Response

Stop the run.

Normal Sheets operations should use the existing authenticated API token. Authentication changes require explicit human approval.

---

## Problem: agent starts editing its own framework

### Examples

- patching OAuth setup code
- changing requested scopes
- changing environment variables
- installing alternate integrations
- relocating credentials

### Response

Stop the run and return to the supported method.

Framework/configuration changes are a separate administrative action and require explicit approval.

## Troubleshooting principle

When something fails, ask:

1. What exact operation was attempted?
2. What exact upstream error was returned?
3. Which layer failed: authentication, authorization, API enablement, request format, or application logic?
4. Can the same supported method be retried after fixing that specific layer?

Avoid changing multiple layers at once. That destroys the evidence needed to identify the real cause.
