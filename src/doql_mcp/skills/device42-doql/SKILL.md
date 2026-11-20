---
name: device42-doql
description: Query the live Device42 instance through the device42-doql MCP server. Use when asked about devices, IP addresses, applications, databases, storage, Kubernetes, discovery, or any other Device42 data, or when writing or running DOQL queries.
---

# Device42 DOQL workflow

## Tools

- `list_schemas(search)`: list view names from the live dictionary. `search` is an optional case-insensitive substring, for example `search="device"`. Always pass `search` to keep output small.
- `get_schema(name)`: return the full dictionary entry for one view, including columns and data types. Output is large (about 28 KB for `view_device_v2`), so request only the views you need.
- `query_doql(query, output_type)`: run a read-only DOQL `SELECT`. `output_type` is `json` (default) or `csv`.

## Steps

1. Find the view with `list_schemas(search=...)`. Do not guess table names. `device` is not a view; the correct name is `view_device_v2`.
2. Check its columns with `get_schema(name)` before writing the query.
3. Run `query_doql` with a `SELECT` and a `LIMIT` for exploration.

Only `SELECT` queries are allowed. The server rejects anything else.

## Naming conventions

- `view_<object>_v1` and `view_<object>_v2`: the newest version is usually `_v2`. Prefer `_v2` when both exist.
- `*_custom_fields` and `*_custom_fields_flat`: user-defined fields for an object type. The `_flat` variant gives one row per field.
- `view_dbb_*`: dependency mapping views.
- `view_appcomp_*`: application component views.
- `view_k8s*`: Kubernetes views.

## Example

Verified against a live instance:

```
SELECT name FROM view_device_v2 LIMIT 5
```

## Notes

- The schema comes from the live dictionary. It can differ between Device42 instances.
- Results can be large. Use `LIMIT`, select only the columns you need, and use `csv` for bulk exports.
