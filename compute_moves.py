#!/usr/bin/env python3


from collections import namedtuple
from dataclasses import asdict, dataclass
from functools import cache, cached_property
import sys


@cache
def n_consistent_assignments(u1, u2, u3, total, N=2):
    """
    return min(max(0, N), number of consistent assignments with number of ones equal to total))
    """

    def w_or_wout(w1, w2, w3, total_with, total_without):
        n1 = n_consistent_assignments(w1, w2, w3, total_with, N)
        assert 0 <= n1 <= N
        return n1 + n_consistent_assignments(w1, w2, w3, total_without, N - n1)

    return (
        0
        if u1 < 0 or u2 < 0 or u3 < 0 or total < 0 or total > 3 or N <= 0
        else 1
        if total == 0
        else 2
        if u1 > total
        else w_or_wout(u1 - 1, u2, u3, total - 1, total)  # take first u1, or don't
        if u1 != 0
        else w_or_wout(0, u2 - 2, u3, total - 2, total)  # take first u2, or don't
        if u2 != 0
        else w_or_wout(0, 0, u3 - 3, total - 3, total)  # take first u3, or don't
    )


@cache
def one_consistent_assignment(u1, u2, u3, total):

    def w_or_wout(delta, w1, w2, w3, total_with, total_without):
        A = one_consistent_assignment(w1, w2, w3, total_with)
        if A is not None:
            return A + delta
        return one_consistent_assignment(w1, w2, w3, total_without)

    asst = (
        None
        if u1 < 0 or u2 < 0 or u3 < 0 or total < 0
        else Delta()
        if total == 0
        else Delta(u1=total)
        if u1 >= total
        else w_or_wout(Delta(u1=1), u1 - 1, u2, u3, total - 1, total)  # take first u1, or don't
        if u1 != 0
        else w_or_wout(Delta(u2=2), 0, u2 - 2, u3, total - 2, total)  # take first u2, or don't
        if u2 != 0
        else w_or_wout(Delta(u3=3), 0, 0, u3 - 3, total - 3, total)  # take first u3, or don't
    )
    if asst is not None:
        assert asst.u1 + asst.u2 + asst.u3 == total
        assert 0 <= asst.u1 <= u1
        assert 0 <= asst.u2 <= u2
        assert 0 <= asst.u3 <= u3
    return asst


@dataclass(frozen=True)
class Delta:
    u1: int = 0
    u2: int = 0
    u3: int = 0
    zero: int = 0
    one: int = 0

    @cached_property
    def values(self):
        return asdict(self).values()

    def __add__(self, delta):
        assert isinstance(delta, Delta)
        return Position(*(s + d for s, d in zip(self.values, delta.values)))

    def __ge__(self, delta):
        if delta is None:
            return True
        assert isinstance(delta, Delta)
        return all(s >= d for s, d in zip(self.values, delta.values))

    def __repr__(self):
        return f"({self.u1}, {self.u2}, {self.u3}, {self.zero}, {self.one})"


class Position(Delta):
    @cached_property
    def components(self):
        return self.u1 + self.u2 // 2 + self.u3 // 3

    @cached_property
    def n_consistent_assignments(self):
        return n_consistent_assignments(self.u1, self.u2, self.u3, 3 - self.one)

    @cached_property
    def one_consistent_assignment(self):
        return one_consistent_assignment(self.u1, self.u2, self.u3, 3 - self.one) + Delta(one=self.one)

    @cached_property
    def legal(self):
        return self.n_consistent_assignments != 0

    # def __repr__(self):
    #     return f"({self.u1}, {self.u2}, {self.u3}, {self.zero}, {self.one}, #{self.n_consistent_assignments})"


C = namedtuple("C", ["priority", "lowerbounds", "rs"])
R = namedtuple("R", ["comparison_result", "delta"])
D = LB = Delta
EDGES = dict(
    u1_u1=C(
        0,
        None,
        (
            R(0, D(u1=-2, u2=2)),
            R(1, D(u1=-2, zero=1, one=1)),
        ),
    ),
    u1_u2=C(
        4,
        None,
        (
            R(0, D(u1=-1, u2=-2, u3=3)),
            R(1, D(u1=-1, u2=-2, zero=2, one=1)),  # u2 is zero
            R(-1, D(u1=-1, u2=-2, zero=1, one=2)),  # u1 is zero
        ),
    ),
    u1_u3=C(
        5,
        None,
        (
            R(0, D(u1=-1, u3=-3, zero=4)),
            R(1, D(u1=-1, u3=-3, zero=3, one=1)),  # u3 is zero
            R(-1, D(u1=-1, u3=-3, zero=1, one=3)),  # u1 is zero
        ),
    ),
    u2_u2=C(
        2,
        None,
        (
            R(0, D(u2=-4, zero=4)),
            R(1, D(u2=-4, zero=2, one=2)),
        ),
    ),
    u2_u3=C(
        6,
        None,
        (
            R(0, D(u2=-2, u3=-3, zero=5)),
            R(1, D(u2=-2, u3=-3, zero=3, one=2)),  # u3 is zero
            R(-1, D(u2=-2, u3=-3, zero=2, one=3)),  # u2 is zero
        ),
    ),
    u3_u3=C(
        3,
        None,
        (
            R(0, D(u3=-6, zero=6)),
            R(1, D(u3=-6, zero=3, one=3)),
        ),
    ),
    u1_zero=C(
        7,
        LB(zero=1),
        (
            R(0, D(u1=-1, zero=1)),  # u1 is zero
            R(1, D(u1=-1, one=1)),  # u1 is one
        ),
    ),
    u2_zero=C(
        8,
        LB(zero=1),
        (
            R(0, D(u2=-2, zero=2)),  # u2 is zero
            R(1, D(u2=-2, one=2)),  # u2 is one
        ),
    ),
    u3_zero=C(
        9,
        LB(zero=1),
        (
            R(0, D(u3=-3, zero=3)),  # u3 is zero
            R(1, D(u3=-3, one=3)),  # u3 is one
        ),
    ),
    u1_one=C(
        10,
        LB(one=1),
        (
            R(0, D(u1=-1, one=1)),  # u1 is one
            R(-1, D(u1=-1, zero=1)),  # u1 is zero
        ),
    ),
    u2_one=C(
        11,
        LB(one=1),
        (
            R(0, D(u2=-2, one=2)),  # u2 is on
            R(-1, D(u2=-2, zero=2)),  # u2 is zero
        ),
    ),
    u3_one=C(
        12,
        LB(one=1),
        (
            R(0, D(u3=-3, one=3)),  # u3 is one
            R(-1, D(u3=-3, zero=3)),  # u3 is zero
        ),
    ),
).items()


ComparisonEdge = namedtuple("ComparisonEdge", ["priority", "comparison", "result_edges"])
ResultEdge = namedtuple("ResultEdge", ["comparison_result", "node"])


@cache
def node(position):
    return Node(position) if position.legal else None


class Node:
    def __init__(self, position):
        assert position.legal
        self.position = position

        # if STACK:
        #     assert position.components < STACK[-1].position.components, (STACK, self)

        # STACK.append(self)

        if self.position.n_consistent_assignments == 1:
            self.comparison_edges = ()
            self.consistent = True
            self.value = 0
        else:
            c_edges = (
                ComparisonEdge(
                    c.priority,
                    comparison,
                    tuple(
                        sorted(
                            (
                                ResultEdge(r.comparison_result, _node)
                                for r in c.rs
                                if (_node := node(position + r.delta)) is not None
                                and _node.consistent
                            ),
                            key=lambda r_edge: (r_edge.node.value, -abs(r_edge.comparison_result)),
                        )
                    ),
                )
                for comparison, c in EDGES
                if self.position >= c.lowerbounds
            )
            c_edges = tuple(
                sorted(
                    (c_edge for c_edge in c_edges if c_edge.result_edges),
                    key=lambda c_edge: (c_edge.result_edges[-1].node.value, c_edge.priority),
                )
            )
            self.comparison_edges = c_edges
            self.consistent = bool(c_edges)
            assert self.consistent
            if self.consistent:
                self.min_edge = c_edges[0]
                self.min_max_edge = self.min_edge.result_edges[-1]
                self.min_max_node = self.min_max_edge.node
                self.value = 1 + self.min_max_node.value

        # assert STACK.pop() is self

    @cached_property
    def play(self):
        def _play():
            nonlocal self
            yield self
            while self.comparison_edges:
                yield (self := self.min_max_node)

        return list(_play())

    def __repr__(self):
        if getattr(self, "comparison_edges", None):
            sym = {-1: "<", 0: "=", 1: ">"}[self.min_max_edge.comparison_result]
            comp = " " + self.min_edge.comparison.replace("_", f" {sym} ")
        else:
            comp = ""
        return f"{self.position}: v{getattr(self, 'value', '-')}{comp}"

    def __str__(self):
        return self.__repr__()


def dump_alg(start):
    with open("moves.py", "w") as sys.stdout:

        def dfs(node):
            if hasattr(node, "visited"):
                return
            node.visited = True
            if node.value == 0:
                data = f"{tuple(node.position.one_consistent_assignment.values)}"
            else:
                c1, c2 = node.min_edge.comparison.split("_")
                data = f"('{c1}', '{c2}')"
                for c_edge in node.comparison_edges:
                    for r_edge in c_edge.result_edges:
                        dfs(r_edge.node)

            print(f"    {node.position}: ({node.value}, {data}),")

        print("from types import MappingProxyType")

        print("moves = MappingProxyType({")
        dfs(start)
        print("})")


n = 100
start = node(Position(u1=n))
# print("\n".join(str(x) for x in start.play))

dump_alg(start)
