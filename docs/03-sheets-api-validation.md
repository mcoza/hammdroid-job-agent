# 03 — Google Sheets API Validation

OAuth authentication and API activation are separate controls. A valid OAuth token does not guarantee the Google Sheets API is enabled for the Cloud project.

## 1. Attempt one harmless API operation

The first test should be intentionally small:

1. create a temporary spreadsheet
2. write a known value
3. read the same value back

Do not change configuration just because the first request fails.

## 2. Recognize the disabled-service error

The initial test in this project returned:

```text
HTTP 403
SERVICE_DISABLED
service=sheets.googleapis.com
```

This meant:

```text
OAuth authentication       working
Token loading              working
Request reached Google     working
Sheets API service         disabled
```

The correct response was to enable **Google Sheets API** in the same Google Cloud project and then retry the exact same test.

No new OAuth flow or framework modification was required.

## 3. Create the temporary spreadsheet

After the API was enabled, spreadsheet creation succeeded.

## 4. Write test values

Use a range that matches the shape of the values being written.

Example:

```text
A1:A2
```

with two rows:

```text
test_value_1
test_value_2
```

A malformed range/value combination can produce an HTTP 400 even when authentication and API access are correct.

## 5. Read the values back

The validation only passes when the same values are returned by a subsequent read.

Expected logical result:

```json
[
  ["test_value_1"],
  ["test_value_2"]
]
```

## 6. What this proves

A successful create → write → read round trip proves:

```text
OAuth identity
    ↓
Stored token
    ↓
Google Sheets API
    ↓
Spreadsheet creation
    ↓
Cell write
    ↓
Cell read
    ↓
Correct data returned
```

## 7. Cleanup and Drive permissions

Creating or editing a spreadsheet through the Sheets API does not imply the token has general Google Drive permissions.

If cleanup through a Drive API operation fails because Drive scope was intentionally not granted, do not automatically expand OAuth permissions just to delete a test artifact. Manual cleanup is acceptable for a one-time validation file.

## Test result for this project

- OAuth: passed
- Sheets API enabled: passed
- Create: passed
- Write/update: passed
- Read-back: passed
- General Drive access: intentionally not granted
