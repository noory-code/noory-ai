from app.errors import ConfigError


def parse_port(value):
    if not isinstance(value, str) or not value.isascii() or not value.isdigit():
        raise ConfigError(f"invalid port: {value!r}")
    port = int(value)
    if not 1 <= port <= 65535:
        raise ConfigError(f"port out of range: {value!r}")
    return port
