#!/usr/bin/env python3

import random
import itertools


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


def random_choice(n, k):
    return tuple(random.sample(range(n), k))


def input(n, one_indices):
    return tuple(1 if i in one_indices else 0 for i in range(n))


def test_find_three_ones():
    # soln = random_choice(100, 3)
    # print(trial(input(100, soln)))

    print(max(trial(input(100, c)) for c in choose(100, 3)))


def comp(x, y):
    return (x > y) - (y > x)


def group(iter, k):
    rank = itertools.count()
    return tuple(tuple(g) for k, g in itertools.groupby(iter, key=lambda g: next(rank) // k))


def find_three_ones(compare):
    twenty_pairs = group(range(40), 2)
    twenty_triples = group(range(40, 100), 3)

    def find_in_groups(groups):
        def f():
            for i, *rest in groups:
                smaller_than_i, equal_to_i, larger_than_i = [], [i], []
                by_result = {-1: smaller_than_i, 0: equal_to_i, 1: larger_than_i}
                for j in rest:
                    by_result[compare(j, i)].append(j)
                if smaller_than_i:
                    yield from equal_to_i
                elif larger_than_i:
                    yield from larger_than_i
        return tuple(f())

    found_in_pairs = find_in_groups(twenty_pairs)
    found_in_triples = find_in_groups(twenty_triples)
    found = found_in_pairs + found_in_triples

    def find_ones_group(monochromatic_groups):
        _found, = find_in_groups(group([c[0] for c in monochromatic_groups], 2))
        return next(g for g in monochromatic_groups if _found in g)

    match len(found):
        case 0:         # must be a (1, 1, 1) triple
            found = find_ones_group(twenty_triples)

        case 1:         # must be a (1, 1) pair, and a (0, 1) pair or a (0, 0, 1) triple
            if len(found_in_pairs) == 0:
                groups = twenty_pairs
            else:
                # all triples are (0, 0, 0)
                groups = tuple(g for g in twenty_pairs if found[0] not in g) + twenty_triples[:1]

            found = found + find_ones_group(groups)

    return found


test_find_three_ones()
