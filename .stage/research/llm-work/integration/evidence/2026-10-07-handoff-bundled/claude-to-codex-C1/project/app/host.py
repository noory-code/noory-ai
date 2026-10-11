from app.errors import ConfigError


def parse_host(value):
    if (
        not isinstance(value, str)
        or not value
        or "." not in value
        or any(character.isspace() for character in value)
    ):
        raise ConfigError(f"invalid host: {value!r}")
    return value
