# Local Runtime: Hermes + Ollama

This document captures the local-agent setup I actually configured for HammDroid and, more importantly, why I chose this architecture.

## Why I wanted local inference

My first constraint was cost. A job-search agent can perform a lot of repetitive work: reading pages, comparing requirements, keeping state, and deciding what to inspect next. I did not want every routine step to require a metered cloud-model request.

The design direction became:

```text
routine repetitive work
→ run locally when practical

ambiguous or high-value review
→ optionally use a stronger cloud model later
```

This is a design goal, not a claim that the local/cloud reviewer pipeline is complete.

Local inference also gives me a system I can inspect directly: I can see which model is loaded, whether it is using the GPU, what endpoint Hermes is calling, and where the model files live.

## Runtime components

The current local path I configured is:

```text
Hermes Agent
    ↓ local provider
http://localhost:11434/v1
    ↓
Ollama
    ↓
local GGUF model
    ↓
NVIDIA GPU
```

The responsibilities are different:

```text
Hermes Agent → agent runtime, tool orchestration, workflow behavior
Ollama       → local model server / inference endpoint
model        → language-model weights used for inference
GPU          → executes the model workload
```

I did not build Hermes or Ollama. My work here is the local configuration and integration between those components.

## Ollama setup

I configured Ollama to keep model files on a dedicated drive rather than the default system-drive location.

```text
model storage → E:\AI\Models
```

That was a practical storage decision. Local model files are large, and I did not want them consuming the primary Windows drive unnecessarily.

During validation, `ollama ps` showed the loaded model running entirely on the GPU.

The model used during this setup was:

```text
hf.co/ornith-ai/Ornith-1.5-9B-GGUF:Q4_K_M
```

The loaded model was approximately 5.6 GB in that quantization.

`Q4_K_M` is a quantized build: the goal is to reduce memory requirements enough for practical local inference while accepting some accuracy loss relative to higher-precision weights.

## Hermes configuration

I configured Hermes with a local provider pointing at Ollama's OpenAI-compatible endpoint:

```text
provider endpoint → http://localhost:11434/v1
```

The agent display name was set to:

```text
HammDroid
```

The initial setup was intentionally minimal rather than enabling every possible integration at once. The terminal backend was local, and the baseline tools were kept around file and terminal access while the runtime was being proven.

I also configured a context setting of approximately 85,000 tokens in Hermes. That number is a **runtime configuration value**, not a benchmark proving that every prompt can use that entire context effectively. Actual usable context still depends on model/runtime support and memory behavior.

## What I used to verify the local path

The important test was not simply that the software installed. I wanted to prove that the components were connected in the intended direction.

```text
Hermes configured for local provider
        ↓
Ollama endpoint reachable
        ↓
model loaded
        ↓
ollama ps reports active model
        ↓
GPU utilization path confirmed
```

This established the local inference layer before adding more automation around it.

## Why I did not use several models immediately

I considered a multi-model design where different models could act as reviewer/judge/executor roles.

I did not make that the baseline architecture because it adds more model memory, routing logic, latency, and debugging paths before the single-model workflow is proven.

My current rule is:

```text
one local model that works
→ prove workflow
→ identify actual weakness
→ add another model only if that weakness justifies it
```

That keeps the project from becoming complicated just because a more elaborate architecture is possible.

## Why Hermes instead of writing an agent framework from scratch

The goal of HammDroid is the job-search workflow, not building another orchestration framework.

Using Hermes lets me work at the integration layer:

```text
model endpoint
+ tools
+ state
+ workflow rules
+ human stops
```

instead of spending the project on recreating agent plumbing.

That also makes the implementation boundary clearer: Hermes is an external runtime; HammDroid is the configuration, integrations, design decisions, and workflow built around it.

## Current boundary

Validated/configured in the local setup:

- Ollama installed and serving a local model
- model storage moved to a dedicated drive
- Ornith 1.5 9B Q4_K_M loaded during testing
- model reported as running on GPU
- Hermes configured against `localhost:11434/v1`
- local terminal backend configured
- HammDroid agent identity/configuration established

Not claimed as complete:

- benchmarked model quality for job classification
- automated model fallback/routing
- multi-model judge/reviewer architecture
- cloud-model oversight pipeline
- autonomous end-to-end job application workflow
