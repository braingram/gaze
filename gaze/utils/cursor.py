#!/usr/bin/env python


class Cursor:
    def __init__(self, x, default=None):
        self._i = 0
        self._x = x
        self._d = default

    def advance(self, n=1):
        self._i += n

    def current(self):
        return self.peek(delta=0)

    def next(self):
        self.advance()
        return self.current()

    def check_index(self, i):
        if i >= len(self._x):
            return len(self._x) - 1
        return i

    def peek(self, delta=1):
        i = self.check_index(self._i + delta)
        return self[i]

    def __call__(self, delta=0):
        return self.peek(delta=delta)

    def __getitem__(self, i):
        if (i >= 0) and (i < len(self._x)):
            return self._x[i]
        return self._d

    def seek(self, index):
        self._i = index

    def reset(self):
        self.seek(0)

    def end(self):
        """
        Returns True if cursor is off the 'end'
        i.e. self._i >= len(self._x)
        """
        return self._i >= len(self._x)
