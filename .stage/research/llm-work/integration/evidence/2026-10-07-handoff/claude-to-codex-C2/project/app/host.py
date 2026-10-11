def parse_host(value):
    if isinstance(value, str) and value and "." in value and not any(
        character.isspace() for character in value
    ):
        return value
    return None
