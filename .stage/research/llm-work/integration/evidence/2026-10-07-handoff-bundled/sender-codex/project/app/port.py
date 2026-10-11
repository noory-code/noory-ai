from app.errors import ConfigError


def parse_port(value):
    """Parse a decimal port number from an ASCII digit string."""
    if not isinstance(value, str) or not value or not value.isascii() or not value.isdecimal():
        raise ConfigError("port must be a digit string")

    digits = value.lstrip("0")
    if not digits or len(digits) > 5:
        raise ConfigError("port must be between 1 and 65535")

    port = int(digits)
    if port > 65535:
        raise ConfigError("port must be between 1 and 65535")
    return port
