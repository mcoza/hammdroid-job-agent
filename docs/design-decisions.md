# Design Decisions and Why I Made Them

HammDroid is not a finished autonomous job-application system. It is a project I am building in layers so I can understand, test, and justify each part before adding the next one.

My main concern has been avoiding two bad extremes:

```text
manual everything
→ repetitive and hard to scale

fully autonomous black box
→ difficult to trust, debug, or control
```

The design I am aiming for sits between those: automate repetitive work, keep the state visible, and stop for the human when the decision is consequential or uncertain.

## 1. Local-first instead of cloud-first

A job-search agent can generate a large amount of routine model traffic. If every page read, comparison, classification, or tool decision goes through a paid API, cost becomes part of every iteration.

I already have hardware capable of running useful local models, so my first design choice was:

```text
routine inference
→ local model

stronger review when it is actually useful
→ optional cloud model later
```

This is partly about cost, but also about control. With a local runtime I can inspect which model is loaded, how much GPU memory it uses, where the model files live, and which endpoint the agent is calling.

I do not need the local model to be the best model available. I need it to be good enough for the repetitive portion of the workflow, with a clear way to escalate uncertain cases later if needed.

## 2. Use Hermes as the agent runtime instead of writing one from scratch

I considered the difference between building the job-search workflow and building an entire agent framework.

Those are not the same project.

Hermes already provides the orchestration layer, so I can focus on:

```text
local model connection
+ tool access
+ workflow behavior
+ structured state
+ human approval boundaries
```

rather than rebuilding tool dispatch, conversation state, and agent plumbing.

That means HammDroid is primarily an **integration and workflow project**. I am not claiming that I wrote Hermes itself.

## 3. Use Ollama as the local model service

I wanted the agent runtime and the model runtime separated cleanly.

The path I configured is:

```text
Hermes
→ local provider endpoint
→ Ollama
→ local GGUF model
→ GPU
```

This separation is useful because Hermes does not need to know how the model is stored or executed internally. It only needs a compatible endpoint.

Likewise, I can change the local model later without redesigning the entire workflow.

I also moved the model storage to a dedicated drive because model files are large and do not need to live on the primary Windows volume.

## 4. Start with one model instead of a model committee

I explored the idea of multiple local models acting as judge/reviewer/executor roles.

That could be useful eventually, but it also adds:

- more VRAM/RAM pressure
- more inference time
- routing logic
- more failure paths
- more questions about which model should override which

I decided that was backwards for the current stage.

My rule is:

```text
prove one-model workflow
→ observe actual weaknesses
→ add another model only if it solves a measured problem
```

I would rather have one understandable pipeline that works than three models whose interaction I cannot yet justify.

## 5. Google Sheets instead of a database

The job-search state I need right now is fundamentally tabular: jobs, companies, status, notes, dates, and related fields.

I considered whether I needed a database and decided I did not yet.

A database would give stronger querying, relations, concurrency, and transaction behavior, but it would also add infrastructure and maintenance before those are real requirements.

Google Sheets gives me something useful for this stage:

```text
structured rows/cells
+ persistent cloud state
+ API access
+ direct human visibility
+ manual correction when needed
```

That last part matters. I do not want the agent's state hidden in a system I have to query just to see what it thinks happened.

If the workflow later grows enough that Sheets becomes the bottleneck, that will be evidence for moving to a database. I do not want to add one just because agent projects often have one.

## 6. API access for state instead of browser-driving the spreadsheet

If HammDroid needs to update a spreadsheet, I would rather have it call the Google Sheets API than automate mouse clicks and cell editing through the browser.

The API path is clearer:

```text
agent
→ OAuth token
→ Sheets API request
→ range/value operation
→ returned state
```

This gives me identifiable failure layers and structured responses.

The OAuth/Sheets setup already proved why this matters: I hit separate failures in credential discovery, OAuth access, Google Cloud service enablement, and request formatting. Those would have been harder to isolate if the spreadsheet itself were being controlled through UI automation.

## 7. Keep credentials outside the repository

Hermes needs OAuth client/token material locally, but those files do not belong in Git.

The separation I want is:

```text
repository
→ documentation and non-secret project material

local Hermes home
→ OAuth client configuration
→ tokens / refresh state
→ runtime-specific local state
```

That is why `.gitignore` excludes the relevant credentials, token files, environment files, browser sessions, and `.hermes` state.

## 8. Human approval is part of the architecture

The goal is not to remove myself from the process entirely.

There are actions where the agent can assist but should stop before making the final decision:

- CAPTCHA
- MFA/passkeys
- legal attestations
- assessments
- questions whose factual answer is not known
- final application submission

The same applies to resume/application content. The agent cannot invent employment, dates, clearances, certifications, skills, or experience.

I think of this as both a safety boundary and a state-integrity boundary. Once bad information enters an automated workflow, it can propagate quickly.

## 9. Build in layers I can troubleshoot

The architecture I am aiming for is intentionally separable:

```text
local inference
      ↓
agent runtime
      ↓
tools / browser interaction
      ↓
structured state API
      ↓
human approval when required
```

Each layer should be testable on its own.

For example:

```text
model does not answer
→ inspect Ollama / model / endpoint

Hermes cannot use local model
→ inspect provider configuration

Google helper cannot authenticate
→ inspect credential path / OAuth

OAuth succeeds but Sheets call fails
→ inspect API enablement / request shape
```

That is the main architectural principle behind HammDroid: add capabilities in a way that still lets me identify which component is failing.

## Current direction

The project is now at the point where the local runtime and the Google Sheets state integration have both been proven separately.

The next meaningful work is not adding more infrastructure. It is connecting those proven pieces into a constrained job-search workflow and testing where the local model is actually good enough versus where human or stronger-model review is needed.
