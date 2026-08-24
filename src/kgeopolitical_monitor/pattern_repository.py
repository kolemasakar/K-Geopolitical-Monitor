"""Pattern persistence abstraction baseline."""


class PatternRepository:
    def __init__(self):
        self._patterns = []

    def add(self, pattern):
        self._patterns.append(pattern)

    def all(self):
        return list(self._patterns)
