from typing import Optional, Any


def expect(value: Optional[Any], message: str) -> Any:
    if value is None:
        raise Exception(message)
    return value
