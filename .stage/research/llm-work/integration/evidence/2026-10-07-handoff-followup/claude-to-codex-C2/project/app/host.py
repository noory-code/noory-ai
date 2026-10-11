def parse_host(value):
    if not isinstance(value, str) or not value or "." not in value:
        return None
    if any(character.isspace() for character in value):
        return None
    return value
