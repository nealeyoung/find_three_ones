#!/usr/bin/env python3

import itertools
import random
from collections import defaultdict

from _table import table

from disjoint_set import make_set


class Partition:
    def __init__(self, indices):
        self.parts = {i: make_set(i) for i in indices}
        self.unknown_parts_by_size = defaultdict(set)
        self.unknown_parts_by_size[1] = set(self.parts.values())

        self.zero_part = make_set()
        self.one_part = make_set()
        self.known_parts = {-1: self.zero_part, 1: self.one_part}

    def equiv(self, i, j):
        return self.parts[i].equiv(self.parts[j])

    def _known(self, part):
        return part.equiv(self.zero_part, self.one_part)

    def _union(self, p1, p2):
        p1, p2 = p1.find(), p2.find()
        if not p1.equiv(p2):
            for p in (p1, p2):
                self.unknown_parts_by_size[p.size()].discard(p)

            p1.union(p2)
            p1 = p1.find()
            if not self._known(p1):
                self.unknown_parts_by_size[p1.size()].add(p1)

    def register_comparison(self, i, j, result):
        p1, p2 = self.parts[i], self.parts[j]
        if result == 0:
            self._union(p1, p2)
            if p1.size() > 3:
                self._union(self.zero_part, p1)
        else:
            self._union(self.known_parts[result], p1)
            self._union(self.known_parts[-result], p2)

    def parts_w_size(self, size, n=None):
        if n == 0:
            return ()
        iterator = self.unknown_parts_by_size[size]
        return iterator if n is None else itertools.islice(iterator, n)

    def parts_w_size_reps(self, size, n=None):
        return (p.i for p in self.parts_w_size(size, n))

    def _signature(self):
        return (
            len(self.unknown_parts_by_size[1]),
            2 * len(self.unknown_parts_by_size[2]),
            3 * len(self.unknown_parts_by_size[3]),
            self.zero_part.size(),
            self.one_part.size(),
        )

    def _table_row(self):
        return table[self._signature()]

    def _data(self):
        return self._table_row()[1]

    def value(self):
        return self._table_row()[0]

    def done(self):
        return self.value() == 0

    def indices_to_compare(self):
        assert not self.done()

        def indices():
            to_compare = self._data()
            for i, ui in zip(range(1, 4), ("u1", "u2", "u3")):
                yield from self.parts_w_size_reps(i, to_compare.count(ui))
            for p, name in zip((self.zero_part, self.one_part), ("zero", "one")):
                if to_compare.count(name):
                    yield p

        indices = tuple(indices())
        assert len(indices) == 2, indices
        return indices

    def solution(self):
        assert self.done()

        parts = self.parts.values()
        soln = self._data()
        sizes = tuple(s for s in range(1, 4) if soln[s - 1])
        ones = tuple(
            p.i
            for p in parts
            if p.equiv(self.one_part) or (p.size() in sizes and not self._known(p))
        )

        assert len(ones) == 3, (ones, self._data())
        return ones


def find_three_ones(compare):
    indices = range(100)
    partition = Partition(indices)

    while not partition.done():
        i, j = partition.indices_to_compare()
        result = compare(i, j)
        partition.register_comparison(i, j, result)

    return partition.solution()
