# Serena Client Configuration Reference

Setup instructions for all supported MCP clients.

## Claude Code

From project root directory:
```bash
claude mcp add serena -- uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context ide-assistant --project "$(pwd)"
```

**Requirements:**
- Claude Code v1.0.52+ (earlier versions don't read MCP system prompts)
- Context `ide-assistant` disables duplicate tools

**Post-Setup:**
Project auto-activates via `--project` flag. Begin working immediately.

## Claude Desktop

Edit `claude_desktop_config.json`:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux (community):** `~/.config/Claude/claude_desktop_config.json`

Access via: File → Settings → Developer → MCP Servers → Edit Config

**Configuration (uvx method):**
```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/oraios/serena",
        "serena", "start-mcp-server",
        "--context", "desktop-app"
      ]
    }
  }
}
```

**With fixed project:**
```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/oraios/serena",
        "serena", "start-mcp-server",
        "--context", "ide-assistant",
        "--project", "/absolute/path/to/project"
      ]
    }
  }
}
```

**Important:** Full quit via File → Exit (closing minimizes to tray).

## Codex (OpenAI)

Add to `~/.codex/config.toml`:
```toml
[mcp_servers.serena]
command = "uvx"
args = ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server", "--context", "codex"]
```

**Post-Launch:**
Say: "Activate the current dir as project using serena"

**Known Issue:** Tools may display as "failed" in UI despite successful execution.

## ChatGPT (Custom GPT via MCPO)

**1. Start Server:**
```bash
uvx mcpo --port 8000 --api-key <YOUR_SECRET_KEY> -- \
  uvx --from git+https://github.com/oraios/serena \
  serena start-mcp-server --context chatgpt --project "$(pwd)"
```

**2. Expose via Cloudflare:**
```bash
cloudflared tunnel --url http://localhost:8000
```

**3. Configure GPT:**
- Create GPT → Add APIs
- Auth: Bearer token with your API key
- Import schema: `<cloudflared_url>/openapi.json`
- Add to schema top:
```json
"servers": [{"url": "<cloudflared_url>"}]
```

**Security:** Never expose API key. Disable `execute_shell_command`.

## Cursor/Windsurf/VSCode

Use context `ide-assistant` or `ide` to avoid tool duplication with built-in capabilities.

Consult client-specific MCP documentation for configuration location.

## Docker (Experimental)

```bash
docker run --rm -i --network host \
  -v /path/to/projects:/workspaces/projects \
  ghcr.io/oraios/serena:latest \
  serena start-mcp-server --transport stdio
```

**Compose:**
```yaml
services:
  serena:
    image: ghcr.io/oraios/serena:latest
    command: serena start-mcp-server --transport stdio
    volumes:
      - ./projects:/workspaces/projects
    network_mode: host
```

## Streamable HTTP Mode

For self-managed server lifecycle:
```bash
uvx --from git+https://github.com/oraios/serena \
  serena start-mcp-server \
  --transport streamable-http \
  --port 9121
```

Connect client to: `http://localhost:9121/mcp`

## Common Arguments

| Argument | Purpose |
|----------|---------|
| `--project <path\|name>` | Pre-activate project |
| `--context <name>` | Set operating context |
| `--mode <name>` | Enable mode (repeatable) |
| `--enable-web-dashboard false` | Disable dashboard |

Dashboard default: `http://localhost:24282/dashboard/index.html`
