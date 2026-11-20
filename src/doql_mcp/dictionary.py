from typing import Any


def extract_schemas(payload: Any) -> dict[str, Any]:
    """Map each view name in the Device42 data dictionary to its entry."""
    if not isinstance(payload, list):
        raise ValueError(f"Expected a list of dictionary entries, got {type(payload).__name__}")

    schemas: dict[str, Any] = {}
    for entry in payload:
        name = entry.get("view") if isinstance(entry, dict) else None
        if not isinstance(name, str):
            raise ValueError("Dictionary entry is missing a string 'view' name")
        if name in schemas:
            raise ValueError(f"Duplicate dictionary view: {name}")
        schemas[name] = entry
    return schemas
