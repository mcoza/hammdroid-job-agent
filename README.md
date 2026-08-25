# HammDroid Job Agent

HammDroid is my local-first job-search agent project.

The idea is not to build a giant autonomous system immediately. I want to automate the repetitive parts of job searching while keeping the workflow understandable, inexpensive to run, and under human control when the decision actually matters.

My approach has been:

```text
prove one layer
→ understand how it works
→ see what problem appears next
→ add only the next piece I actually need
```

This repository documents the pieces I have really configured and tested: the local AI runtime, Hermes Agent integration, Google OAuth/Sheets state, the failures I hit while connecting them, and the design decisions behind the architecture.

## Why I am building it this way

### Local-first instead of cloud-first

A job-search agent can make a lot of routine model calls. I do not want every classification, page review, or orchestration step to consume paid API tokens if my own machine can handle the repetitive work.

The direction I am aiming for is:

```text
routine repetitive work
→ local model

uncertain / higher-value review
→ optional stronger cloud model later
```

That keeps cost down and gives me more visibility into what is running locally.

### Hermes instead of writing an agent framework

My goal is the job-search workflow, not rebuilding agent orchestration from scratch.

Hermes provides the agent/runtime layer so I can focus on:

```text
local inference
+ tools
+ persistent state
+ workflow rules
+ human approval boundaries
```

I am not claiming that I wrote Hermes itself.

### Google Sheets instead of a database

The state I need right now is simple and tabular. I want the agent to read/write it through an API, but I also want to be able to open the same state myself and understand it immediately.

So my current reasoning is:

```text
Google Sheets
→ structured rows/cells
→ persistent state
→ API-accessible
→ directly human-readable/editable
```

I do not currently need enough concurrency, relational structure, or transactional behavior to justify maintaining a database just because I can.

## Current architecture

The pieces I have proven separately look like this:

```text
                    LOCAL INFERENCE

Hermes Agent
    ↓ local provider
http://localhost:11434/v1
    ↓
Ollama
    ↓
local GGUF model
    ↓
GPU

                    STRUCTURED STATE

Hermes Agent
    ↓
Google Workspace helper
    ↓
OAuth 2.0 token
    ↓
Google Sheets API
    ↓
job-search state
```

The next step is connecting these proven pieces into the actual constrained job-search workflow rather than adding more infrastructure first.

## Local runtime I configured

The current setup includes:

- Ollama serving a local model on the machine
- model storage moved to `E:\AI\Models`
- `hf.co/ornith-ai/Ornith-1.5-9B-GGUF:Q4_K_M` used during the setup
- the loaded model reported by `ollama ps` as running on the GPU
- Hermes configured to use the local endpoint `http://localhost:11434/v1`
- local terminal backend
- minimal initial tool setup rather than enabling everything at once
- HammDroid used as the Hermes agent name

I configured Hermes with a large context setting during setup, but I treat that as a configuration value rather than claiming a measured effective context length.

See [Local Runtime: Hermes + Ollama](docs/local-runtime.md).

## Google Sheets integration I tested

The Google integration work included:

- Google Desktop OAuth client setup
- resolving where the Hermes helper actually expected its credential files
- handling OAuth testing/test-user access
- reducing unrelated Google Workspace permissions
- enabling `sheets.googleapis.com`
- diagnosing `403 access_denied`
- diagnosing `403 SERVICE_DISABLED`
- diagnosing an HTTP 400 malformed write request
- validating a spreadsheet **create → write → read** round trip

The useful part was learning to separate the failure layers:

```text
credential exists but helper cannot find it
→ path resolution

403 access_denied
→ OAuth consent / test-user configuration

403 SERVICE_DISABLED
→ Google Cloud API enablement

HTTP 400 malformed write
→ request construction
```

`append` behavior has not been separately validated.

See [Google Sheets Integration](docs/google-sheets-integration.md).

## Human control is part of the design

I am not trying to make the agent silently answer every application question or submit anything it is unsure about.

The intended workflow stops for:

- CAPTCHA
- MFA/passkeys
- legal attestations
- assessments
- factual questions the system cannot verify
- final application submission

The system also must not invent employers, dates, experience, clearances, certifications, skills, or application answers.

That is both a safety boundary and a data-integrity boundary.

## What this project currently demonstrates

| Area | Hands-on work represented |
|---|---|
| **Local AI runtime** | Ollama model storage/runtime, GPU-backed local inference, local model endpoint |
| **Agent integration** | Hermes local-provider configuration, local terminal/tool baseline, runtime separation from model serving |
| **OAuth 2.0** | Desktop client setup, test-user troubleshooting, local credential/token handling |
| **Google Sheets API** | API activation, authenticated create/write/read validation, request-format troubleshooting |
| **Integration troubleshooting** | separating path, authentication, service-enable, and request-format failures |
| **Architecture decisions** | local-first inference, Sheets instead of premature database infrastructure, API state instead of UI-driven spreadsheet editing |
| **Control boundaries** | explicit human stops for consequential or unverifiable application actions |

## Current boundary

### Configured / tested

- local Ollama inference path
- Hermes connected to the local model endpoint
- model loading on GPU
- local model storage configuration
- Google Desktop OAuth setup
- Hermes credential-path troubleshooting
- Sheets API activation
- create/write/read spreadsheet validation
- repository secret exclusions

### Not claimed as complete

- automatic job discovery
- job-page parsing
- deduplication
- job-fit classification benchmarks
- browser-driven application completion
- multi-model judge/reviewer architecture
- automated local-to-cloud escalation
- autonomous application submission

## Repository structure

```text
README.md

docs/
  design-decisions.md
  local-runtime.md
  google-sheets-integration.md
```

Start with [Design Decisions and Why I Made Them](docs/design-decisions.md) for the reasoning behind the project.

No OAuth client secrets, tokens, authorization codes, browser sessions, or local Hermes credential state are stored in this repository.
