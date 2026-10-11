from app.errors import ConfigError


def parse_host(value):
    if (
        not isinstance(value, str)
        or not value
        or "." not in value
        or any(char.isspace() for char in value)
    ):
        raise ConfigError(f"invalid host: {value!r}")
    return value
