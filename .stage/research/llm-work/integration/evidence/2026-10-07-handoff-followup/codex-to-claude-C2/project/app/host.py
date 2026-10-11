def parse_host(value):
    """Return a host containing a dot and no whitespace, or None if invalid."""
    if not isinstance(value, str) or not value or "." not in value:
        return None
    if any(ch.isspace() for ch in value):
        return None
    return value
