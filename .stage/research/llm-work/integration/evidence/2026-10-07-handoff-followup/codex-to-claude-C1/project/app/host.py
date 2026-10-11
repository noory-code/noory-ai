from app.errors import ConfigError


def parse_host(value):
    """Return a host name: a nonempty string containing a dot and no whitespace."""
    if not isinstance(value, str) or not value or "." not in value:
        raise ConfigError("host must be a nonempty string containing a dot")
    if any(ch.isspace() for ch in value):
        raise ConfigError("host must not contain whitespace")
    return value
