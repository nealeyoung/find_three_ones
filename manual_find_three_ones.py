#!/usr/bin/env python3

import random
import itertools


##########################################################################################
##########################################################################################


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

    assert frozenset(alg_soln) == soln, (soln, alg_soln)
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


def input(n, one_indices):
    return tuple(1 if i in one_indices else 0 for i in range(n))


def test_find_three_ones():
    print(max(trial(input(100, c)) for c in choose(100, 3)))


##########################################################################################
##########################################################################################


def group(iter, k):
    rank = itertools.count()
    return tuple(tuple(g) for k, g in itertools.groupby(iter, key=lambda g: next(rank) // k))


def find_three_ones(compare):
    twenty_pairs = group(range(40), 2)
    twenty_triples = group(range(40, 100), 3)

    def find_in_groups(groups):
        for group in groups:
            i, *rest = group
            smaller_than_i, equal_to_i, larger_than_i = [], [i], []
            by_result = {-1: smaller_than_i, 0: equal_to_i, 1: larger_than_i}
            for j in rest:
                by_result[compare(j, i)].append(j)
            if smaller_than_i:
                yield from equal_to_i
            elif larger_than_i:
                yield from larger_than_i

    found_in_pairs = tuple(find_in_groups(twenty_pairs))
    found_in_triples = tuple(find_in_groups(twenty_triples))
    found = found_in_pairs + found_in_triples

    if len(found) == 3:
        return found

    if len(found) == 0:  # must be a (1, 1, 1) triple
        monochromatic_groups = twenty_triples
    else:
        assert len(found) == 1  # must be a (1, 1) pair, and a (0, 1) pair or a (0, 0, 1) triple
        monochromatic_groups = tuple(g for g in twenty_pairs if found[0] not in g)

    ones = (
        tuple(find_in_groups(group([c[0] for c in monochromatic_groups], 2)))
        or monochromatic_groups[-1]  # only happens if len(monochromatic_groups) is odd
    )
    return found + next(g for g in monochromatic_groups if ones[0] in g)


##########################################################################################
##########################################################################################


test_find_three_ones()
