# doql-mcp

An [MCP](https://modelcontextprotocol.io) server that exposes read-only [Device42](https://www.device42.com) DOQL queries and the live Device42 data dictionary to MCP clients such as VS Code Copilot Chat or Claude Desktop.

## Features

- **Run DOQL queries** with the `query_doql` tool. Only a single `SELECT` statement is accepted; semicolons and other statements are rejected.
- **Discover views and columns** with the `list_schemas` and `get_schema` tools, which read the dictionary loaded from the Device42 instance at startup.
- **Browse the data dictionary** as MCP resources: `device42://dictionary` for the full dictionary and `device42://schema/<view>` for each view.
- **DOQL workflow prompt** named `device42-doql`, served from the skill file packaged at `src/doql_mcp/skills/device42-doql/SKILL.md`.
- **Two transports**: `stdio` (default) for local clients and `streamable-http` for remote or containerized use.

## Requirements

- Python 3.10 or newer
- Network access to a Device42 instance
- Device42 credentials: an API Client key and secret, or a username and password

## Installation

```bash
pip install .
```

For development, install in editable mode:

```bash
pip install -e .
```

This installs the `doql-mcp` command.

## Configuration

The server reads its configuration from environment variables.

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `D42_BASE_URL` | Yes | | Base URL of the Device42 instance, for example `https://d42.example.com`. |
| `D42_CLIENT_KEY` | One auth pair | | API Client key. Used with `D42_CLIENT_SECRET` to request a bearer token. |
| `D42_CLIENT_SECRET` | One auth pair | | API Client secret. Must be set together with `D42_CLIENT_KEY`. |
| `D42_USERNAME` | One auth pair | | Username for HTTP basic auth. Used with `D42_PASSWORD`. |
| `D42_PASSWORD` | One auth pair | | Password for HTTP basic auth. Used with `D42_USERNAME`. |
| `D42_VERIFY_SSL` | No | `true` | Set to `false` to skip TLS certificate verification. Accepts `1`, `true`, `yes`, or `on` as true. |
| `D42_TIMEOUT` | No | `30` | HTTP timeout in seconds. |

If both an API Client pair and a username/password pair are set, the API Client pair is used.

## Usage

Start the server with the default stdio transport:

```bash
export D42_BASE_URL=https://d42.example.com
export D42_CLIENT_KEY=your-key
export D42_CLIENT_SECRET=your-secret
doql-mcp
```

Serve over streamable HTTP instead:

```bash
doql-mcp --transport streamable-http --host 127.0.0.1 --port 8000
```

| Option | Default | Description |
| --- | --- | --- |
| `--transport` | `stdio` | `stdio` or `streamable-http`. |
| `--host` | `127.0.0.1` | Bind address for `streamable-http`. |
| `--port` | `8000` | Port for `streamable-http`. |

On startup the server downloads the data dictionary from Device42 and fails if it cannot. Logs are written to stderr, so stdout stays clean for the stdio transport.

You can also run the package as a module with `python -m doql_mcp`.

### MCP client configuration

Example stdio configuration for an MCP client:

```json
{
  "mcpServers": {
    "device42-doql": {
      "command": "doql-mcp",
      "env": {
        "D42_BASE_URL": "https://d42.example.com",
        "D42_CLIENT_KEY": "your-key",
        "D42_CLIENT_SECRET": "your-secret"
      }
    }
  }
}
```

## Tools

| Tool | Arguments | Description |
| --- | --- | --- |
| `query_doql` | `query: str`, `output_type: "json" \| "csv"` (default `json`) | Runs a read-only DOQL `SELECT` and returns the result. |
| `list_schemas` | `search: str` (optional) | Lists view names, filtered by a case-insensitive substring. |
| `get_schema` | `name: str` | Returns the dictionary entry for one view, including its columns and data types. |

Example DOQL query:

```
SELECT name FROM view_device_v2 LIMIT 5
```

## Docker

Build the image:

```bash
docker build -t doql-mcp .
```

Run it with the streamable HTTP transport on port 8000, which is the image default:

```bash
docker run --rm -p 8000:8000 \
  -e D42_BASE_URL=https://d42.example.com \
  -e D42_CLIENT_KEY=your-key \
  -e D42_CLIENT_SECRET=your-secret \
  doql-mcp
```

The container runs as a non-root user (`app`, UID 1000).

## Project layout

```
src/doql_mcp/
  __main__.py    Entry point for `python -m doql_mcp`
  cli.py         Argument parsing, startup, and transport selection
  client.py      Async HTTP client for the Device42 API (auth, dictionary, DOQL)
  config.py      Environment-based settings and authentication checks
  dictionary.py  Converts the dictionary payload into a view-name mapping
  server.py      MCP server, tools, resources, and prompt
  skills/        DOQL workflow guide served as the device42-doql prompt
data/dd.json     Sample data dictionary snapshot (not read at runtime)
.github/skills/  Copy of the DOQL skill for VS Code Copilot (keep in sync with skills/)
Dockerfile       Container image definition
```

## Development

Run the server locally against a Device42 instance using the configuration above. The project has no test suite yet.

## Notes

- The schema comes from the live Device42 instance and can differ between deployments.
- DOQL result sets can be large. Use `LIMIT`, select only the columns you need, and prefer `csv` for bulk exports.
