from dataclasses import asdict, dataclass
from functools import cache, cached_property


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
        return one_consistent_assignment(self.u1, self.u2, self.u3, 3 - self.one) + Delta(
            one=self.one
        )

    @cached_property
    def legal(self):
        return self.n_consistent_assignments != 0

    # def __repr__(self):
    #     return f"({self.u1}, {self.u2}, {self.u3}, {self.zero}, {self.one}, #{self.n_consistent_assignments})"


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
