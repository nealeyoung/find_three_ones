# find_three_ones
An algorithm to compute an optimal algorithm to find three ones, in a 100-element 0/1 array, using a minimum number of comparisons.

The algorithm that computes the algorithm is in recompute_table.py .  Running that script
takes a few minutes.  It computes an optimal algorithm for the problem and outputs the
algorithm (suitably encoded in a table) to the file _table.py .

The file find_three_ones.py imports _table.py and uses it to reconstruct and implement
the optimal algorithm (see the find_three_ones function there).

You can test find_three_ones by running test_find_three_ones.py .
