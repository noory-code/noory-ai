def parse_host(value):
    """Return a host name containing a dot, or None for invalid input."""
    if not isinstance(value, str) or not value or "." not in value:
        return None
    if any(ch.isspace() for ch in value):
        return None
    return value
