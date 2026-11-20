import argparse
import asyncio
import logging
import sys
from typing import Any, Sequence

from .client import Device42Client
from .config import Device42Settings
from .dictionary import extract_schemas
from .server import build_server

logger = logging.getLogger("doql_mcp")


async def load_schemas(settings: Device42Settings) -> dict[str, Any]:
    async with Device42Client(settings) as client:
        return extract_schemas(await client.get_dictionary())


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="doql-mcp", description="Device42 DOQL MCP server")
    parser.add_argument("--transport", choices=["stdio", "streamable-http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1", help="bind address for streamable-http")
    parser.add_argument("--port", type=int, default=8000, help="port for streamable-http")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    # Logs go to stderr so stdout stays clean for the stdio transport.
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)

    settings = Device42Settings.from_env()
    schemas = asyncio.run(load_schemas(settings))
    logger.info("Loaded %d Device42 schemas", len(schemas))

    server = build_server(settings, schemas)
    if args.transport == "stdio":
        server.run("stdio")
    else:
        server.run("streamable-http", host=args.host, port=args.port)
