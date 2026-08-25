# Retained Hermes Runtime Evidence

This file is a sanitized excerpt from the local Hermes CLI output captured while building HammDroid. It is included to show the external runtime that was actually present during the integration work rather than describing an abstract agent stack.

## CLI availability

```text
hermes --help

Hermes Agent - AI assistant with tool-calling capabilities

Selected commands observed in the local CLI:

chat
model
setup
auth
status
cron
project
doctor
verify
security
config
skills
tools
computer-use
mcp
sessions
monitoring
dashboard
serve
desktop
logs
```

Selected invocation options observed:

```text
-z, --oneshot PROMPT
-m, --model MODEL
--provider PROVIDER
--reasoning LEVEL
-t, --toolsets TOOLSETS
--skills SKILLS
--safe-mode
--tui
--cli
```

The CLI described `--oneshot` as a mode that sends one prompt and prints only the final response to stdout, while still loading tools, memory, rules, and project context. That made it relevant to the design idea of driving a repeatable job-search workflow from scripts instead of relying only on an interactive chat session.

## Boundary

Hermes Agent is an external runtime. This evidence does not imply that HammDroid implemented the Hermes CLI, model runtime, tool-calling engine, or desktop application. The HammDroid work represented in this repository is the Python prototype, workflow/state design, configuration, and integration troubleshooting around that runtime.
