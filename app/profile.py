def display_name(first: str, middle: str | None, last: str) -> str:
    return f"{first} {middle[0].upper()}. {last}"
