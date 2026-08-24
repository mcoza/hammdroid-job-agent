# Agent Guardrails

The main operational lesson from this setup was that the agent needed strong boundaries around troubleshooting and authentication.

## Core rule

> Use the intended capability. If it fails, inspect the exact error, retry once only when there is a clear reason, then stop and report.

## Required behavior

The agent should:

- use existing authenticated API tooling when available
- prefer deterministic API operations over browser UI automation
- report exact upstream errors
- stop at authentication or permission boundaries
- ask for approval before changing system configuration

## Forbidden autonomous behavior

The agent should not, without explicit approval:

- edit Hermes source code
- patch skills or setup scripts
- modify environment variables
- change OAuth scopes
- start a fresh OAuth flow
- copy or relocate credential files
- install alternate integrations
- substitute an MCP, browser workflow, custom script, or driver for the requested method
- trigger Google login, passkey, MFA, or account-recovery flows during normal Sheets work

## Failure sequence

Use:

```text
Expected method
      ↓
Attempt
      ↓
Inspect exact error
      ↓
One justified retry
      ↓
STOP + report
```

Do not use:

```text
Failure
  ↓
Invent workaround
  ↓
Modify framework
  ↓
Change authentication
  ↓
Try unrelated tools
  ↓
Keep looping
```

## Google-specific rule

Normal spreadsheet operations should use the already-authenticated Google Sheets API path.

If the API returns:

- `401`
- `403`
- insufficient scope
- service disabled
- token invalid

then the agent should report the exact error and stop. It should not automatically re-authenticate or expand permissions.

## Browser security prompts

The agent must never interact autonomously with:

- passwords
- passkeys
- MFA codes
- security keys
- CAPTCHA
- account recovery
- legal attestations

If one appears, control returns to the human operator.

## Application truthfulness rule

The agent must never represent education, certifications, coursework, labs, homelabs, or portfolio projects as professional employment experience.

It must not invent employers, dates, years of experience, clearances, salaries, certifications, skills, or application answers.

## Why this matters

The dangerous failure mode was not a single bad API request. It was the agent treating a failure as permission to redesign its environment.

The guardrails separate:

- **using an approved capability** from
- **changing the system that provides that capability**.
