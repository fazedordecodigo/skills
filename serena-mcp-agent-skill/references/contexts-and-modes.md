# Serena Contexts and Modes Reference

## Contexts

Set at startup via `--context <name>`. Cannot be changed during session.

| Context | Purpose | Tool Adjustments |
|---------|---------|-----------------|
| `desktop-app` | Claude Desktop (default) | Full toolset, no assumptions about client capabilities |
| `claude-code` | Claude Code CLI | Disables tools duplicating Claude Code built-ins |
| `ide-assistant` | IDE integrations (Cursor, VSCode, etc.) | Minimal tools, assumes IDE handles basics |
| `ide` | Generic IDE context | Basic file ops/shell assumed handled by IDE |
| `codex` | OpenAI Codex | Adjusted for Codex MCP quirks |
| `chatgpt` | ChatGPT via MCPO | Optimized for HTTP API access |
| `agent` | Autonomous agent frameworks | Full toolset for maximum autonomy |
| `oaicompat-agent` | Local servers (Llama.cpp) | OpenAI-compatible tool descriptions |

**Single-Project Contexts:** `ide` and `claude-code` define `single_project: true`, disabling `activate_project` when a project is provided at startup.

## Modes

Set at startup or switched dynamically via `switch_modes` tool. Multiple can be active.

| Mode | Purpose | Effect |
|------|---------|--------|
| `editing` | Direct code modification | Optimizes for precise changes (default) |
| `interactive` | Conversational workflow | Back-and-forth interaction (default) |
| `planning` | Analysis and planning | Focus on strategy before implementation |
| `one-shot` | Single-response tasks | Complete in one response, often with `planning` |
| `no-onboarding` | Skip onboarding | Assumes memories exist or aren't needed |
| `onboarding` | Initial project setup | Auto-triggered first session (usually) |
| `no-memories` | Disable memory tools | For ephemeral sessions |

**Defaults:** `interactive` + `editing` active unless explicitly specified.

**Mode Specification:**
```bash
--mode interactive --mode editing --mode no-memories
```

**Incompatible Combinations:**
- `interactive` + `one-shot` (conflicting interaction styles)
- `no-memories` + `onboarding` (onboarding writes memories)

## Context Selection Guide

| Scenario | Context |
|----------|---------|
| Claude Desktop app | `desktop-app` |
| Claude Code in terminal | `claude-code` |
| Cursor/VSCode/IDE extensions | `ide-assistant` or `ide` |
| OpenAI Codex | `codex` |
| ChatGPT Custom GPT | `chatgpt` |
| Custom agent (Agno, LangGraph) | `agent` |
| Local LLM server | `oaicompat-agent` |

## Mode Combination Patterns

| Workflow | Modes |
|----------|-------|
| Standard development | `interactive` + `editing` |
| Planning session | `interactive` + `planning` |
| Generate report/analysis | `planning` + `one-shot` |
| Quick fix, no chat | `editing` + `one-shot` |
| Analysis only | `planning` + `no-memories` |
| Fresh start (no prior context) | `interactive` + `editing` + `no-onboarding` |

## Configuration Files

**Global:** `~/.serena/serena_config.yml`
```yaml
enabled_tools:
  - find_symbol
  - replace_symbol_body
  # ...
excluded_tools:
  - execute_shell_command
```

**Project:** `.serena/project.yml`
```yaml
name: my-project
language: python
read_only: false
excluded_tools:
  - execute_shell_command
```

## Custom Contexts/Modes

Create custom definitions:
```bash
serena context create my-context
serena context edit my-context

serena mode create my-mode
serena mode edit my-mode
```

Definitions stored in `~/.serena/` as YAML.

## Dynamic Mode Switching

During session, instruct agent:
- "Switch to planning and one-shot modes"
- "Enable read-only analysis mode"

Agent uses `switch_modes` tool to change active modes.
