# Local Runtime

This is the local AI setup I configured for HammDroid.

## Setup

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

Each part has a different job:

```text
Hermes Agent → agent and tool layer
Ollama       → serves the local model
model        → generates the responses
GPU          → runs the model workload
```

I did not build Hermes or Ollama. My work here was installing, configuring, and connecting them for HammDroid.

## Why I wanted a local model

The main reason was cost. A job-search agent can do a lot of small repetitive tasks, and I do not want every one of those tasks to require a paid API call.

Running locally also gives me more visibility into the setup. I can check what model is loaded, whether it is using the GPU, where the model files are stored, and which endpoint Hermes is using.

I may still use a cloud model later for harder or uncertain decisions. That part is not built yet.

## Ollama

I moved the Ollama model storage to:

```text
E:\AI\Models
```

I did that because model files are large and I have more room on that drive than on the main Windows drive.

The model used during setup was:

```text
hf.co/ornith-ai/Ornith-1.5-9B-GGUF:Q4_K_M
```

`ollama ps` showed the model loaded on the GPU during testing.

The model was about 5.6 GB in that quantization.

`Q4_K_M` is a quantized version of the model. The point is to use less memory so the model is practical to run locally. The tradeoff is some loss in quality compared with higher-precision versions.

## Hermes

I configured Hermes to use Ollama through:

```text
http://localhost:11434/v1
```

I used a local terminal backend and kept the first tool setup small while I was getting the runtime working.

The Hermes agent name was set to:

```text
HammDroid
```

I also set a large context value during setup. I treat that as a Hermes setting, not proof that the model can actually use the full amount well in every prompt.

## What I checked

I wanted to verify more than just whether the programs installed.

The path I checked was:

```text
Hermes points at local provider
→ Ollama endpoint is available
→ model is loaded
→ ollama ps shows the active model
→ model is running on the GPU
```

That gave me a working local model path before adding more integrations.

## Why I stayed with one model

I looked at using several local models for different roles, such as one doing the task and another reviewing it.

I decided not to start there because it would add more memory use, more waiting, and more routing logic before I even knew what the single-model workflow was missing.

For now the plan is simple:

```text
get one model working
→ use it in the real workflow
→ find the actual weak points
→ add another model only if it helps with one of those weak points
```

## Current status

Tested or configured:

- Ollama installed and serving a local model
- model files moved to `E:\AI\Models`
- Ornith 1.5 9B Q4_K_M loaded during testing
- model reported on the GPU by `ollama ps`
- Hermes pointed at `localhost:11434/v1`
- local terminal backend configured
- HammDroid agent name configured

Not finished:

- job-fit quality testing
- automatic fallback to another model
- multi-model review
- cloud-model review path
- full job-search workflow
