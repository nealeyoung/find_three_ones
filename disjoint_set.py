

def make_set(i=None):
    return DisjointSet(i)


class DisjointSet:
    """e.g. https://en.wikipedia.org/wiki/Disjoint-set_data_structure"""

    def __init__(self, i=None):
        self._size = 0 if i is None else 1
        self.i = i
        self._parent = self

    def find(self):
        while not self.is_root():
            self, self._parent = self._parent, self._parent._parent
        return self

    def union(self, other):
        r1, r2 = self.find(), other.find()
        if r1 is not r2:
            if r1._size < r2._size:
                r1, r2 = r2, r1
            r2._parent = r1
            r1._size += r2._size

    def is_root(self):
        return self._parent is self

    def equiv(self, *others):
        return any(self.find() == other.find() for other in others)

    def size(self):
        return self.find()._size
