import os
from dataclasses import dataclass

def _env_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Device42Settings:
    base_url: str
    verify_ssl: bool = True
    timeout: float = 30.0
    username: str | None = None
    password: str | None = None
    client_key: str | None = None
    client_secret: str | None = None

    @classmethod
    def from_env(cls) -> "Device42Settings":
        base_url = os.environ.get("D42_BASE_URL")
        if not base_url:
            raise RuntimeError("Missing required environment variable: D42_BASE_URL")
        verify_ssl = _env_bool("D42_VERIFY_SSL", True)
        timeout = float(os.environ.get("D42_TIMEOUT", "30"))

        client_key = os.environ.get("D42_CLIENT_KEY")
        client_secret = os.environ.get("D42_CLIENT_SECRET")
        if client_key or client_secret:
            if not (client_key and client_secret):
                raise RuntimeError("D42_CLIENT_KEY and D42_CLIENT_SECRET must both be set")
            return cls(
                base_url=base_url.rstrip("/"),
                verify_ssl=verify_ssl,
                timeout=timeout,
                client_key=client_key,
                client_secret=client_secret,
            )

        username = os.environ.get("D42_USERNAME")
        password = os.environ.get("D42_PASSWORD")
        if username and password:
            return cls(
                base_url=base_url.rstrip("/"),
                verify_ssl=verify_ssl,
                timeout=timeout,
                username=username,
                password=password,
            )

        raise RuntimeError(
            "Set D42_CLIENT_KEY and D42_CLIENT_SECRET (API Client token auth), "
            "or D42_USERNAME and D42_PASSWORD (basic auth)"
        )
