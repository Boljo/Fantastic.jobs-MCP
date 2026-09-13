# Fantastic.jobs MCP Server

A small local MCP server that lets Claude search fresh job postings through the [Fantastic.jobs API](https://developer.fantastic.jobs/). Ask Claude something like *"find data engineer jobs in Chicago from the last week"* and it calls the API for you.

## How it works

```
Claude Desktop  ──stdio──▶  job_server.py  ──▶  client_call.py  ──HTTPS──▶  data.fantastic.jobs
```

| File | Role |
|---|---|
| `client_call.py` | Talks to the API. `callout()` sends the request and returns the raw JSON. |
| `job_server.py` | The MCP server. Wraps `callout()` in a `search_jobs` tool and trims the response to a few fields. |
| `main.py` | Manual test script for poking at the API from the terminal. Not used by Claude. |
| `.env` | Holds your API key. Git-ignored. |

Claude Desktop launches `job_server.py` as a background process and talks to it over stdin/stdout. You never start it yourself.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)
- A Fantastic.jobs API key (from your subscriptions page)
- Claude Desktop (or Claude Code)

## Setup

```bash
git clone <this-repo>
cd linkedin
uv sync
echo 'linkedin_api=YOUR_KEY_HERE' > .env
```

## Test it in the terminal

Call the tool function directly, no MCP involved:

```bash
uv run python -c "from job_server import search_jobs; print(search_jobs('Data Engineer', time_frame='7d'))"
```

A list of jobs means the API call, key, and field trimming all work. An empty list `[]` just means no matches for that search.

To test through the real MCP protocol, use the Inspector (needs Node.js):

```bash
uv run mcp dev job_server.py
```

## Connect to Claude Desktop

Open **Settings → Developer → Edit Config** and add an entry under `mcpServers`. Use full paths: Claude Desktop is launched from the Dock and can't see your shell's `PATH`.

```json
{
  "mcpServers": {
    "fantastic-jobs": {
      "command": "/Users/YOU/.local/bin/uv",
      "args": ["--directory", "/absolute/path/to/linkedin", "run", "job_server.py"]
    }
  }
}
```

Find your uv path with `which uv`. Then fully quit Claude Desktop (Cmd+Q) and reopen it. `search_jobs` should appear in the tools list.

For Claude Code instead:

```bash
claude mcp add fantastic-jobs -- uv --directory /absolute/path/to/linkedin run job_server.py
```

## The tool

```
search_jobs(title, location="", time_frame="24h", limit=10)
```

| Parameter | Notes |
|---|---|
| `title` | Required. Keyword match. Use quotes for an exact phrase, and `OR` to combine: `"Data Engineer" OR "Analytics Engineer"` |
| `location` | Full names only, no abbreviations: `Chicago, Illinois, United States`. Same `OR` syntax. Results are global if omitted. |
| `time_frame` | `1h`, `24h`, or `7d` |
| `limit` | Max results per call. Each result costs API credits. |

Each job comes back trimmed to: `title`, `organization`, `url`, `date_posted`, `locations_derived`, `ai_core_responsibilities`. Edit `FIELDS` in `job_server.py` to change this. The full API response has 50+ fields including AI-extracted skills, salary, and company data.

## Gotchas

- **Never `print()` inside `job_server.py`.** stdout is the channel Claude talks over; a stray print corrupts it. Use `print(..., file=sys.stderr)` for debugging.
- **Restart Claude Desktop after any code or config change.** The server process is spawned at launch and reads the key once at import.
- **`.zshrc` doesn't reach Claude Desktop.** That's why the key lives in `.env`, which `load_dotenv()` picks up regardless of how the server was started.
- **401 Unauthorized** means the key didn't arrive. Check `.env` exists, has the right name (`linkedin_api`), and that no stale `env` block in the Claude config is overriding it.
- **Server shows as failed** in Claude Desktop: Settings → Developer has per-server logs. It's almost always the uv path, the project path, or a missing key.

## Security

`.env` is in `.gitignore`. Confirm before your first commit with `git check-ignore -v .env`. If a key ever leaks, rotate it from your Fantastic.jobs subscriptions page.