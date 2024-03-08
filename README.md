# find_three_ones
An algorithm to compute an optimal algorithm to find three ones, in a 100-element 0/1 array, using a minimum number of comparisons.

Inspired by https://cs.stackexchange.com/questions/166885/find-1s-in-almost-all-0-array-using-comparisons-only .

The algorithm that computes the algorithm is in recompute_table.py .  Running that script
takes a few minutes.  It computes an optimal algorithm for the problem and outputs the
algorithm (suitably encoded in a table) to the file _table.py .

The file find_three_ones.py imports _table.py and uses it to reconstruct and implement
the optimal algorithm (see the find_three_ones function there).

You can test find_three_ones by running test_find_three_ones.py .

---------------------------

Rough ideas:

Suppose you run some algorithm A for the problem on some input X (which A only accesses by comparisons).
After A has done some comparisons, the information in the outcomes can be captured by a partition
of the elements (the integers 1..100) into equivalence classes, where two elements are equivalent
iff the outcomes of the comparisons so far imply that the they must be equal.

That is, if, in every legal input X that is consistent with the outcomes so far, X[i] equals X[j].

In addition, it may be known, for one of the parts in this partition, that each i in the part
has X[i] = 1.  Likewise, it may be known for one other part in the partition that each
i in that part has X[i] = 0.

Furthermore, in this partition there will be at most one part that has size 4 or larger,
because, in any part of size 4 or larger, the only possible value for X[i] for i's in the part
is 0.  (Because all X[i]'s in the part have to have the same value, and only three X[i]'s
in the input can have value 1.)

Define the _signature_ of such a partition to be a 5-tuple (u1, u2, u3, n_zero, n_one) of integers, 
with the following meanings:

* n_zero is the number of elements that are known to equal 0 (all of which must be in one part)
* n_one is the number of elements that are known to equal 1 (all of which must be in another part)
* u1 is the number of unknown elements in parts of size 1 (i.e. elements that have not yet been compared)
* u2 is the number of unknown elements that are in parts of size 2
* u3 is the number of unknown elements that are in parts of size 3

(By an _unknown_ element we mean one that is not yet known to have value 0 or 1.)

Note that there can only be one part with size > 3, so the signature determines the partition
(modulo the particular names of the indices in each part, which we don't need to care about).

In finding the optimal algorithm, we imagine that the algorithm plays a zero-sum game against
an adversary, where the algorithm gets to choose what comparison to make at each step,
while the adversary then gets to choose the outcome of the comparison.  The game stops when 
the outcomes so far suffice to determine the input.  The algorithm then pays the adversary
one dollar for each comparison made.  The algorithm wants to minimize the payment,
the adversary wants to maximize it.

We want to compute the value of this game.  Although the obvious representation of the state
of the game at any point is the set of all comparisons and outcomes so far, we may as well
assume the state of the game is specified just by the _signature_ of the current partition.
(Any two states with the same signature are essentially interchangeable, by renaming the elements
appropriately.)

The number of possible signatures is large but not too large.  Note that the "n_one" parameter
has value in (0, 1, 2, 3), and that the sum of the values in the signature must equal 100.
Hence, there are less than 4 * 100^3 = 4,000,000 possible signatures.

We represent the min-max game tree for the game using a directed acyclic graph (DAG) whose elements 
are the possible signatures. (See e.g. https://cs.stackexchange.com/questions/6363/nim-game-tree-minimax ).
Then, using dynamic programming on this DAG, we compute the optimal play for the algorithm
and for the adversary.

We then encode that algorithm in a table with one row for each signature, specifying the 
comparison the algorithm should use given the signature of the current partition.
Note that the comparison is specified by giving a pair of kinds of parts.
E.g. the table may specify the comparison as the string "u2, u3",
meaning: compare some element i from a size-2 part to some element j from a size-3 part.
Any element in any size-2 part will do for i, and any element in any size-3 part will do for j.

If you look at the table in _table.py, you'll see that it has less than 10,000 rows.
We've used a heuristic to compact the table (remove rows that can easily be deduced).
For example, we omit rows for terminal parts (where the game is done), as those can
quickly be detected by some other means.  Likewise, we omit the rows for entries
with comparison "u1, u1", which is the most common entry.  Generally, we omit some
rows chosen so that, if the algorithm looks for a row and doesn't find it, we have
some simple rules for computing what it should be.


