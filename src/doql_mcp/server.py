import json
import re
from importlib.resources import files
from typing import Any, Literal
from urllib.parse import quote

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.mcpserver.resources.types import TextResource

from .client import Device42Client
from .config import Device42Settings

SERVER_NAME = "device42-doql"
DICTIONARY_URI = "device42://dictionary"
SCHEMA_URI_PREFIX = "device42://schema/"
SELECT_PATTERN = re.compile(r"^\s*select\b", re.IGNORECASE)


def schema_uri(name: str) -> str:
    return SCHEMA_URI_PREFIX + quote(name, safe="")


def build_server(settings: Device42Settings, schemas: dict[str, Any]) -> MCPServer:
    server = MCPServer(
        name=SERVER_NAME,
        instructions=(
            "Device42 DOQL access. Use list_schemas and get_schema (or the schema resources) to learn "
            "table and column names, then run read-only DOQL SELECT queries with the query_doql tool."
        ),
    )

    server.add_resource(
        TextResource(
            uri=DICTIONARY_URI,
            name="dictionary",
            description="Full Device42 data dictionary",
            mime_type="application/json",
            text=json.dumps(schemas, indent=2, default=str),
        )
    )
    for name, definition in schemas.items():
        server.add_resource(
            TextResource(
                uri=schema_uri(name),
                name=name,
                description=f"Device42 schema '{name}'",
                mime_type="application/json",
                text=json.dumps(definition, indent=2, default=str),
            )
        )

    @server.tool()
    async def query_doql(query: str, output_type: Literal["json", "csv"] = "json") -> str:
        """Run a read-only DOQL SELECT query against Device42 and return the results."""
        if not SELECT_PATTERN.match(query) or ";" in query:
            raise ToolError("Only a single DOQL SELECT query is allowed (no semicolons).")
        try:
            async with Device42Client(settings) as client:
                return await client.run_doql(query, output_type)
        except httpx.HTTPStatusError as exc:
            raise ToolError(f"Device42 returned {exc.response.status_code}: {exc.response.text}") from exc

    skill_text = files("doql_mcp").joinpath("skills", "device42-doql", "SKILL.md").read_text(encoding="utf-8")

    @server.prompt(name="device42-doql", description="Device42 DOQL workflow guide")
    def device42_doql_skill() -> str:
        return skill_text

    @server.tool()
    async def list_schemas(search: str = "") -> str:
        """List Device42 DOQL view names, optionally filtered by a case-insensitive substring."""
        needle = search.lower()
        return json.dumps(sorted(name for name in schemas if needle in name.lower()), indent=2)

    @server.tool()
    async def get_schema(name: str) -> str:
        """Return the live data dictionary entry for one Device42 DOQL view as JSON."""
        if name not in schemas:
            raise ToolError(f"Unknown schema: {name}")
        return json.dumps(schemas[name], indent=2, default=str)

    return server
