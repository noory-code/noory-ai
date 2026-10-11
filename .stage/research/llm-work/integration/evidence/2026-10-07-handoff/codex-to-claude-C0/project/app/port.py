from app.errors import ConfigError


def parse_port(value):
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
        raise ConfigError("port must be a digit string from 1 to 65535")

    try:
        port = int(value)
    except ValueError as exc:
        raise ConfigError("port must be a digit string from 1 to 65535") from exc

    if not 1 <= port <= 65535:
        raise ConfigError("port must be a digit string from 1 to 65535")

    return port
