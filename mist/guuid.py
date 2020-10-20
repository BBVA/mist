import uuid


def guuid() -> str:
    return uuid.uuid4().hex

__all__ = ("guuid", )
