# Serena Tools Reference

Complete taxonomy of Serena's 35+ tools organized by functional category.

## Semantic Code Retrieval (LSP-powered)

These tools leverage the Language Server Protocol for structural understanding:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `get_symbols_overview` | High-level summary of top-level symbols in a file | Initial architectural understanding, avoid reading entire files |
| `find_symbol` | Global/local search for symbols by name/substring | Locate function/class definitions precisely |
| `find_referencing_symbols` | Find all locations referencing a symbol | Impact analysis before refactoring |
| `jet_brains_find_symbol` | JetBrains-specific symbol search | When using JetBrains IDE integration |
| `jet_brains_find_referencing_symbols` | JetBrains-specific reference finder | JetBrains IDE refactoring workflows |
| `jet_brains_get_symbols_overview` | JetBrains-specific symbol overview | JetBrains IDE initial analysis |

## Symbolic Code Editing

Surgical modifications preserving structural integrity:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `replace_symbol_body` | Replace full symbol definition | Rewriting function logic while preserving signature |
| `insert_after_symbol` | Insert content after symbol definition | Adding new functions, helper code |
| `insert_before_symbol` | Insert content before symbol definition | Adding imports, decorators, comments |
| `rename_symbol` | Rename symbol throughout codebase | Safe global renaming via LSP refactoring |

## Line-Based Editing

Direct file manipulation when symbolic tools aren't applicable:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `replace_lines` | Replace line range with new content | Modifying specific code blocks |
| `insert_at_line` | Insert content at specific line | Adding content at precise locations |
| `delete_lines` | Delete a range of lines | Removing code sections |
| `replace_content` | Replace content with optional regex | Pattern-based replacements |

## File System Operations

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `list_dir` | List files/directories recursively | Exploring project structure |
| `read_file` | Read file within project | Examining file contents (use sparingly) |
| `find_file` | Find files by path patterns | Locating specific files |
| `create_text_file` | Create or overwrite files | Generating new files |
| `search_for_pattern` | Search for patterns in project | Finding code patterns, TODOs, etc. |

## Project Management

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `activate_project` | Activate project by name/path | Switching or initializing projects |
| `onboarding` | Perform initial project analysis | First-time project setup |
| `check_onboarding_performed` | Check if onboarding was done | Before assuming memories exist |
| `get_current_config` | Print active configuration | Debugging, verifying context/modes |
| `remove_project` | Remove project from Serena config | Cleanup |
| `restart_language_server` | Restart LSP after external edits | When files changed outside Serena |

## Memory Management

Durable project knowledge persisted in `.serena/memories/`:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `write_memory` | Store named memory for future sessions | Saving contracts, schemas, progress |
| `read_memory` | Retrieve memory by name | Loading prior context |
| `list_memories` | List all project memories | Discovering available context |
| `delete_memory` | Remove a memory | Cleanup obsolete memories |
| `prepare_for_new_conversation` | Generate continuation summary | Before switching to new chat |
| `summarize_changes` | Document changes made | Session-end documentation |

## Execution

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `execute_shell_command` | Run arbitrary shell commands | Build, test, git operations |

**Security Warning:** This tool enables arbitrary code execution. Disable in `excluded_tools` for untrusted contexts or set `read_only: true`.

## Thinking/Self-Reflection Tools

Prompt agent self-evaluation:

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `think_about_collected_information` | Evaluate if enough info gathered | Before proceeding with implementation |
| `think_about_task_adherence` | Check if still on track | During long operations |
| `think_about_whether_you_are_done` | Final completion check | Before declaring task complete |

## Mode/Context Control

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `switch_modes` | Activate different modes | Changing operational focus mid-session |
| `initial_instructions` | Load Serena's usage instructions | If agent isn't using tools correctly |

## Tool Selection Strategy

**Priority Order (Prefer Higher):**
1. **Symbolic tools** (`find_symbol`, `replace_symbol_body`) - Most efficient, LSP-powered
2. **Line-based tools** (`replace_lines`, `insert_at_line`) - When symbols don't apply
3. **Full file operations** (`read_file`, `create_text_file`) - Last resort, token-heavy

**Anti-Patterns:**
- Reading entire files when `get_symbols_overview` suffices
- Using `replace_content` when `replace_symbol_body` works
- Skipping `find_referencing_symbols` before renaming
- Not using memories for cross-session persistence
