from app.errors import ConfigError


def parse_host(value):
    if (
        not isinstance(value, str)
        or not value
        or "." not in value
        or any(ch.isspace() for ch in value)
    ):
        raise ConfigError("host must be a nonempty string containing a dot and no whitespace")

    return value
