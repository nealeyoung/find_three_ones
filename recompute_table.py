#!/usr/bin/env python3


from collections import namedtuple
from functools import cache, cached_property
import sys

from position import Position, Delta

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
            R(0, D(u2=-2, one=2)),  # u2 is one
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
    with open("_table.py", "w") as sys.stdout:
        with open("_left_out.py", "w") as left_out:

            def dfs(node):
                if hasattr(node, "visited"):
                    return
                node.visited = True
                if node.value == 0:
                    data = tuple(node.position.one_consistent_assignment.values)
                else:
                    data = tuple(node.min_edge.comparison.split("_"))
                    for c_edge in node.comparison_edges:
                        for r_edge in c_edge.result_edges:
                            dfs(r_edge.node)

                posn = node.position
                row = f"    {node.position}: ({node.value}, {data}),"
                print(
                    row,
                    file=left_out
                    if (
                        node.value == 0   # can determine this from position
                        or (data == ("u2", "u2") and posn.u1 <= 1)
                        or data == ("u1", "u1")
                    )
                    else sys.stdout,
                )

            print("table = {")
            dfs(start)
            print("}")


n = 100
start = node(Position(u1=n))
# print("\n".join(str(x) for x in start.play))

dump_alg(start)
