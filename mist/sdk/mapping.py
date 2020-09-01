class _Mapped(dict):

    def __init__(self):
        super().__init__()

    def set(self, name: str, value: object):
        setattr(self, name, value)

    def get(self, name: str) -> object or None:
        return getattr(self, name, None)

mapped = _Mapped()


__all__ = ("mapped", )
