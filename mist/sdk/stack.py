class _Stack(list):

    def __init__(self):
        super(_Stack, self).__init__()
        self.append({"MistBaseNamespace": True})

stack = _Stack()


__all__ = ("stack", )
