#!/usr/bin/env python3

import random

from find_three_ones import find_three_ones


def trial(input):
    soln = frozenset(i for i, b in enumerate(input) if b == 1)
    assert len(input) == 100
    assert len(soln) == 3

    n_comparisons = 0

    def compare(i, j):
        nonlocal n_comparisons
        n_comparisons += 1
        return (input[i] > input[j]) - (input[i] < input[j])

    alg_soln = find_three_ones(compare)

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


def test_find_three_ones():

    # soln = random_choice(100, 3)
    # print(trial(input(100, soln)))

    print(max(trial(input(100, c)) for c in choose(100, 3)))


test_find_three_ones()
