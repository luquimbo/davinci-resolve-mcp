# Claude Desktop Setup Guide

Step-by-step instructions for connecting Claude Desktop to DaVinci Resolve through the MCP server.

## Prerequisites

1. **DaVinci Resolve 18+** installed and running (Free or Studio edition).
2. **Python 3.11+** installed. Verify with:
   ```bash
   python3 --version
   ```
3. **Claude Desktop** installed with MCP support.

## Step 1: Install the MCP Server

Choose one of the following methods:

### Option A: pip (recommended)

```bash
pip install davinci-resolve-mcp
```

### Option B: uv

```bash
uv pip install davinci-resolve-mcp
```

### Option C: From source (development)

```bash
git clone https://github.com/luquimbo/davinci-resolve-mcp.git
cd davinci-resolve-mcp
uv sync
```

## Step 2: Verify the Installation

Make sure DaVinci Resolve is open with a project loaded, then run:

```bash
python scripts/check_resolve.py
```

If installed from PyPI, you can also verify the CLI entry point:

```bash
davinci-resolve-mcp --help
```

## Step 3: Configure Claude Desktop

Open the Claude Desktop configuration file:

**macOS**:
```bash
open ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows**:
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux**:
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

Add the `davinci-resolve` server to the `mcpServers` section:

### If installed from PyPI

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "davinci-resolve-mcp"
    }
  }
}
```

### If installed from source

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/davinci-resolve-mcp", "davinci-resolve-mcp"]
    }
  }
}
```

Replace `/path/to/davinci-resolve-mcp` with the actual path to your cloned repository.

### If using a virtual environment

```json
{
  "mcpServers": {
    "davinci-resolve": {
      "command": "/path/to/venv/bin/davinci-resolve-mcp"
    }
  }
}
```

## Step 4: Restart Claude Desktop

Close and reopen Claude Desktop completely. The MCP server will start automatically when Claude needs it.

## Step 5: Verify the Connection

In a new Claude conversation, ask something like:

> What version of DaVinci Resolve is running?

Claude should be able to call the `resolve_get_version` tool and return the version number.

You can also try:

> List all projects in my Resolve database.

> What timelines are in my current project?

## Troubleshooting

### "DaVinci Resolve is not running"

**Cause**: Resolve is not open, or the scripting bridge cannot connect.

**Fix**:
1. Open DaVinci Resolve and wait for it to fully load.
2. Open a project (some API calls require an active project).
3. Try again.

### "Could not import DaVinciResolveScript"

**Cause**: The scripting modules are not found at the expected platform path.

**Fix**:
1. Verify Resolve is installed (not just downloaded).
2. Check that the scripting modules exist at the platform path:
   - **macOS**: `/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules/`
   - **Windows**: `C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules\`
   - **Linux**: `/opt/resolve/Developer/Scripting/Modules/`
3. On macOS, verify the Resolve version matches (the path changes between major versions only if Resolve is installed in a non-standard location).

### "command not found: davinci-resolve-mcp"

**Cause**: The package is not installed, or the Python scripts directory is not on your PATH.

**Fix**:
1. Reinstall: `pip install davinci-resolve-mcp`
2. If using a virtual environment, make sure it is activated, or use the full path to the command in your Claude Desktop config.
3. On macOS, you may need to add `~/.local/bin` to your PATH:
   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

### Tools return empty results

**Cause**: No project is open, or no timeline is active.

**Fix**:
1. Open a project in DaVinci Resolve.
2. Create or open a timeline.
3. For media pool tools, ensure clips exist in the current folder.
4. For Color/Gallery/Fusion tools, ensure you are on the appropriate page (some features are page-specific).

### Connection drops after Resolve restart

**Expected behavior**: The MCP server auto-reconnects. The next tool call after a Resolve restart may take a moment as the health check detects the stale reference and reconnects. No manual intervention needed.

### Claude Desktop does not show the tools

**Cause**: Configuration file syntax error or wrong command path.

**Fix**:
1. Validate your JSON config file (use a JSON linter).
2. Verify the command works in your terminal: `davinci-resolve-mcp` (should output nothing and wait for stdin, since it uses stdio transport).
3. Check Claude Desktop logs for MCP connection errors.
4. Restart Claude Desktop after any config change.

## Example Prompts

Once connected, try these with Claude:

- "Open the project called 'Wedding Edit' in DaVinci Resolve."
- "Create a new timeline called 'Rough Cut' and add all clips from the current folder."
- "Set the render format to H.265 in MP4, output to my Desktop, and start rendering."
- "Add a Blue marker at the current playhead position with the note 'Review this section'."
- "What are the color correction nodes on the clip called 'Interview_01'?"
- "Export a LUT from the grade on 'Hero_Shot' to my Desktop."
- "Switch to the Color page and grab a still."
