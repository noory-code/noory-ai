def parse_host(value):
    if not isinstance(value, str) or not value or "." not in value or any(c.isspace() for c in value):
        return None
    return value
