from agent.schemas import UserQuery
from pydantic import ValidationError


REFUSED_KEYWORDS = [
    "stock", "invest", "medical", "diagnose", "weapon",
    "illegal", "hack", "kill", "suicide",
]


def validate_input(raw_query: str) -> tuple[bool, str, UserQuery | None]:
    try:
        validated = UserQuery(query=raw_query)
    except ValidationError as e:
        return False, f"Invalid input: {e.errors()[0]['msg']}", None

    lower_q = validated.query.lower()
    for kw in REFUSED_KEYWORDS:
        if kw in lower_q:
            return False, f"Refused: query appears outside the music recommendation scope (matched '{kw}').", None

    return True, "OK", validated
