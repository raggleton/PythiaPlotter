#List of test samples:

### test_2to1:
    Ultra simple, does 2 incoming (1,2) to 1 outgoing (3). Good for testing mothers.

### test_1to2:
    Ultra simple, does 1 incoming (1) to 2 ougoing (2,3). Good for testing daughters.

### test_3to1to2:
    Does 3 incoming (1,2,3) to one intermediate (4) to two outgoing (5, 6). Good for testing simple mother + daughters.

### test_3to2to2:
    Like 3to1to2, Does 3 incoming (1,2,3) to one intermediate (4) to two outgoing (5, 6). In addition, (1) also decays to (7).

### test_5to2to3:
    Has 3 incoming to (1,2,3) an intermediate (6), 2 incoming (4, 5) to another intermediate (7). 6 decays to (8, 9). (7) decays to (9, 10). Designed to test more complicated structures