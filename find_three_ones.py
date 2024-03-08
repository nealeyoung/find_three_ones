#!/usr/bin/env python3

import itertools
import random
from collections import defaultdict, namedtuple
from dataclasses import dataclass
from functools import cache

from moves import moves


class UnionFind:
    def __init__(self, i=None):
        self._size = 0 if i is None else 1
        self.i = i
        self.parent = self

    def is_root(self):
        return self.parent is self

    def root(self):
        if not self.is_root():
            self.parent = self.parent.root()
        return self.parent

    def merge(self, other):
        r1, r2 = self.root(), other.root()
        if r1 is not r2:
            if r1._size < r2._size:
                r1, r2 = r2, r1
            r2.parent = r1
            r1._size += r2._size

    def equivalent(self, other):
        return self.root() == other.root()

    @property
    def size(self):
        return self.root()._size


class Partition:
    def __init__(self, indices):
        self.indices = indices
        self.nodes = {i: UnionFind(i) for i in self.indices}
        self.zero_node = UnionFind()
        self.one_node = UnionFind()
        self.known_nodes = {-1: self.zero_node, 1: self.one_node}
        self.unknown_roots_by_size = defaultdict(set)
        self.unknown_roots_by_size[1] = set(self.nodes.values())

    def _merge(self, node1, node2):
        r1, r2 = node1.root(), node2.root()
        if r1 is not r2:
            self.unknown_roots_by_size[r1.size].discard(r1)
            self.unknown_roots_by_size[r2.size].discard(r2)
            r1.merge(r2)
            r1 = r1.root()
            if r1 not in (self.zero_node.root(), self.one_node.root()):
                self.unknown_roots_by_size[r1.size].add(r1)

    def equivalent(self, i, j):
        return self.nodes[i].equivalent(self.nodes[j])

    def known(self, node):
        test = node.equivalent
        return test(self.zero_node) or test(self.one_node)

    def register_comparison(self, i, j, result):
        node1, node2 = self.nodes[i], self.nodes[j]
        if result == 0:
            self._merge(node1, node2)
            if node1.size > 3:
                self._merge(self.zero_node, node1)
        else:
            self._merge(self.known_nodes[result], node1)
            self._merge(self.known_nodes[-result], node2)

    def indices_w_size(self, size, n=None):
        if n == 0:
            return ()
        generator = (
            i for i, node in self.nodes.items() if node.size == size and not self.known(node)
        )
        return generator if n is None else itertools.islice(generator, n)

    def root_indices_w_size(self, size, n=None):
        if n == 0:
            return ()
        generator = (root.i for root in self.unknown_roots_by_size[size])
        return generator if n is None else itertools.islice(generator, n)

    def _signature(self):
        return (
            len(self.unknown_roots_by_size[1]),
            2 * len(self.unknown_roots_by_size[2]),
            3 * len(self.unknown_roots_by_size[3]),
            self.zero_node.size,
            self.one_node.size,
        )

    def _move(self):
        return moves[self._signature()]

    def value(self):
        return self._move()[0]

    def _data(self):
        return self._move()[1]

    def done(self):
        return self.value() == 0

    def indices_to_compare(self):
        assert not self.done()
        move = self._data()
        indices = []
        indices.extend(self.root_indices_w_size(1, move.count("u1")))
        indices.extend(self.root_indices_w_size(2, move.count("u2")))
        indices.extend(self.root_indices_w_size(3, move.count("u3")))
        if move.count("zero"):
            indices.append(self.zero_node.i)
        if move.count("one"):
            indices.append(self.one_node.i)
        # print(move, indices)
        try:
            i, j = indices
        except ValueError:
            assert False, (indices, move)
        return i, j

    def solution(self):
        assert self.done()

        _Position = namedtuple("_Position", ["u1", "u2", "u3", "zero", "one"])

        ones = [i for i, node in self.nodes.items() if self.one_node.equivalent(node)]
        posn = _Position(*self._data())

        if posn.u1:
            ones.extend(self.indices_w_size(1))
        if posn.u2:
            ones.extend(self.indices_w_size(2))
        if posn.u3:
            ones.extend(self.indices_w_size(3))

        assert len(ones) == 3
        return ones


def alg(compare):
    indices = range(100)
    partition = Partition(indices)

    while not partition.done():
        i, j = partition.indices_to_compare()
        sig = partition._signature()
        assert not partition.equivalent(i, j), (sig, (i, j))
        result = compare(i, j)
        # print(f"{sig} {partition._move()}: compare{(i, j)}->{result}", flush=True)
        partition.register_comparison(i, j, result)
        assert sig != partition._signature()

    return partition.solution()


def trial(input):
    soln = frozenset(i for i, b in enumerate(input) if b == 1)
    assert len(input) == 100
    assert len(soln) == 3

    n_comparisons = 0

    def compare(i, j):
        n_comparisons += 1
        return (input[i] > input[j]) - (input[i] < input[j])

    alg_soln = alg(compare)

    assert frozenset(alg_soln) == soln
    return n_comparisons


def choose(n, k):
    if not (0 <= k <= n):
        return
    if k == 0:
        yield ()
        return
    for c in choose(n - 1, k):
        yield c
    for c in choose(n - 1, k - 1):
        yield c + (n - 1,)


def random_choice(n, k):
    return tuple(random.sample(range(n), k))


def input(n, one_indices):
    return tuple(1 if i in one_indices else 0 for i in range(n))


print("imported moves, starting trial", flush=True)

# soln = random_choice(100, 3)

# print(trial(input(100, soln)))

print(max(trial(input(100, c)) for c in choose(100, 3)))
