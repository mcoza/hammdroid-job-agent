# HammDroid Job Agent

HammDroid is a local job-search agent project I have been building piece by piece.

The goal is to automate the repetitive parts of job searching without turning it into a huge system that I cannot easily follow or troubleshoot. I also want most routine AI work to run locally so I am not paying for an API call every time the agent needs to do something simple.

Right now the project is mostly about getting the underlying pieces working together:

- local model serving with Ollama
- Hermes Agent using the local model
- Google OAuth
- Google Sheets API access
- keeping job-search state somewhere both the agent and I can read
- setting clear points where the agent has to stop and ask me

## Why I chose this setup

### Local model first

A job-search agent can make a lot of small model calls. Running those locally makes more sense to me for routine work when my computer can already handle it.

The plan is to use the local model for normal work and leave room for a stronger cloud model later when something is uncertain or worth a second opinion.

That cloud review path is not built yet.

### Hermes for the agent layer

I did not want to spend the project writing an agent framework from scratch. Hermes already handles the agent and tool side, so I can spend my time on the job-search workflow, integrations, and figuring out where the system needs human input.

I did not build Hermes itself.

### Google Sheets for state

The data I need right now is basic job tracking data such as company, role, status, dates, links, and notes.

Google Sheets is enough for that. The agent can access it through an API and I can still open the same sheet myself and see what is there.

I considered a database, but I do not have a database-sized problem yet. If the project grows to the point where I need better concurrency, relationships between records, or more complicated history, then a database would make more sense.

## Current setup

### Local model path

```text
Hermes Agent
    ↓
http://localhost:11434/v1
    ↓
Ollama
    ↓
Ornith 1.5 9B Q4_K_M
    ↓
NVIDIA GPU
```

During setup I configured:

- Ollama model storage at `E:\AI\Models`
- `hf.co/ornith-ai/Ornith-1.5-9B-GGUF:Q4_K_M`
- Hermes local provider at `http://localhost:11434/v1`
- local terminal backend
- a small initial tool set instead of enabling everything at once
- HammDroid as the Hermes agent name

`ollama ps` showed the model loaded on the GPU during testing.

I also set a large context value in Hermes during setup. I treat that as a setting, not proof that the model can use that entire context effectively in practice.

More detail is in [Local Runtime](docs/local-runtime.md).

### Google Sheets path

```text
Hermes Agent
    ↓
Google Workspace helper
    ↓
OAuth 2.0
    ↓
Google Sheets API
    ↓
job-search sheet
```

I worked through several separate problems while setting this up:

- Hermes was looking for the OAuth files in a different path than I first expected
- Google OAuth returned `403 access_denied` while the app was in testing mode
- the Sheets API returned `403 SERVICE_DISABLED` before it was enabled in the Google Cloud project
- a later write returned HTTP 400 because the request format was wrong

After fixing those issues, I tested a small round trip:

```text
create spreadsheet
→ write values
→ read values back
```

That worked. I have not separately tested append behavior yet.

More detail is in [Google Sheets Integration](docs/google-sheets-integration.md).

## Why I keep human stops in the workflow

There are parts of an application where I do not want the agent guessing or acting on its own.

The plan is to stop for:

- CAPTCHA
- MFA or passkeys
- legal attestations
- assessments
- factual questions the system cannot verify
- final application submission

It also cannot invent employers, dates, experience, clearances, certifications, skills, or application answers.

## What I have actually tested

- Ollama serving a local model
- model files stored on a separate drive
- model loaded on the GPU
- Hermes connected to the Ollama endpoint
- local Hermes terminal setup
- Google Desktop OAuth setup
- Hermes credential path troubleshooting
- Google Sheets API activation
- spreadsheet create, write, and read test
- keeping OAuth secrets and local runtime files out of Git

## What is not finished

- automatic job discovery
- job-page parsing
- deduplication
- tested job-fit scoring
- browser-driven application completion
- multi-model review setup
- automatic local-to-cloud escalation
- autonomous application submission

## Repo layout

```text
README.md

docs/
  design-decisions.md
  local-runtime.md
  google-sheets-integration.md
```

[Design Decisions](docs/design-decisions.md) has more detail on why I made these choices.

No OAuth client secrets, tokens, authorization codes, browser sessions, or local Hermes credential files are stored in this repo.
